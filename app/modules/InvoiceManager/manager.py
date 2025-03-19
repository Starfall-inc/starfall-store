from flask import render_template, current_app
from datetime import datetime, timedelta
import uuid
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from app.models.models import Order, OrderDetail, User
from io import BytesIO
import locale
import math


class EcommerceInvoiceGenerator:
    """
    A class to generate e-commerce styled invoices similar to Flipkart
    """

    def __init__(self, order_id):
        self.order_id = order_id
        self.order = None
        self.user = None
        self.order_details = None
        self.store_info = None
        self.theme_colors = None
        self.invoice_number = None

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple for ReportLab"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def fetch_order_data(self):
        """
        Fetch all necessary data for the invoice from the database
        """
        try:
            self.order = Order.query.get(self.order_id)
            if not self.order:
                return False

            self.user = User.query.get(self.order.user_id)
            if not self.user:
                return False

            self.order_details = OrderDetail.query.filter_by(order_id=self.order_id).all()

            # Generate a unique invoice number
            self.invoice_number = f"{self.order_id}-{uuid.uuid4().hex[:6].upper()}"

            # Store info with branding elements
            self.store_info = {
                "name": current_app.config.get("SHOP_NAME", "Your Store"),
                "email": current_app.config.get("SHOP_EMAIL", "contact@example.com"),
                "phone": current_app.config.get("SHOP_PHONE", "+1234567890"),
                "address": current_app.config.get("SHOP_ADDRESS", "123 Main St, City"),
                "logo": current_app.config.get("LOGO", "/static/images/mascot.png"),
                "currency": current_app.config.get("CURRENCY", "USD"),
                "currency_symbol": current_app.config.get("CURRENCY_SYMBOL", "$"),
                "tax_rate": current_app.config.get("TAX_RATE", 0),
                "reg_number": current_app.config.get("COMPANY_REG_NUMBER", ""),
                "tax_number": current_app.config.get("COMPANY_TAX_NUMBER", ""),
                "bank_name": current_app.config.get("BANK_NAME", ""),
                "bank_account": current_app.config.get("BANK_ACCOUNT", ""),
                "swift_code": current_app.config.get("SWIFT_CODE", ""),
            }

            # Theme colors
            primary_color = current_app.config.get("PRIMARY_COLOR", "#3498db")
            self.theme_colors = {
                "primary": self.hex_to_rgb(primary_color),
                "secondary": self.hex_to_rgb(current_app.config.get("SECONDARY_COLOR", "#2c3e50")),
                "background": self.hex_to_rgb(current_app.config.get("BACKGROUND_COLOR", "#ffffff")),
                "dark": self.hex_to_rgb(current_app.config.get("DARK_COLOR", "#333333")),
                "primary_hex": primary_color
            }

            return True
        except Exception as e:
            print(f"Error fetching order data: {e}")
            return False

    def number_to_words(self, number):
        """Convert a number to words format"""
        locale.setlocale(locale.LC_ALL, '')

        # Split the number into whole and decimal parts
        whole_part = int(number)
        decimal_part = int(round((number - whole_part) * 100))

        # Convert whole part to words
        words = ""
        if whole_part == 0:
            words = "zero"
        elif whole_part == 1:
            words = "one"
        elif whole_part == 2:
            words = "two"
        elif whole_part < 20:
            words_dict = {
                3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
                15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen"
            }
            words = words_dict[whole_part]
        elif whole_part < 100:
            tens = whole_part // 10
            ones = whole_part % 10
            tens_dict = {
                2: "twenty", 3: "thirty", 4: "forty", 5: "fifty",
                6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"
            }
            words = tens_dict[tens]
            if ones > 0:
                words += " " + self.number_to_words(ones)
        elif whole_part < 1000:
            hundreds = whole_part // 100
            remainder = whole_part % 100
            words = self.number_to_words(hundreds) + " hundred"
            if remainder > 0:
                words += " and " + self.number_to_words(remainder)
        elif whole_part < 1000000:
            thousands = whole_part // 1000
            remainder = whole_part % 1000
            words = self.number_to_words(thousands) + " thousand"
            if remainder > 0:
                words += " " + self.number_to_words(remainder)
        else:
            millions = whole_part // 1000000
            remainder = whole_part % 1000000
            words = self.number_to_words(millions) + " million"
            if remainder > 0:
                words += " " + self.number_to_words(remainder)

        # Format final result
        result = words.upper()
        if decimal_part > 0:
            result += f" {self.store_info['currency']} AND {decimal_part} CENTS"
        else:
            result += f" {self.store_info['currency']}"

        return result

    def generate_pdf_bytes(self):
        """
        Generate a PDF invoice similar to e-commerce platforms like Flipkart
        """
        if not self.fetch_order_data():
            return None

        # Create a BytesIO buffer
        buffer = BytesIO()

        # Use A4 for more space
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=15 * mm, leftMargin=15 * mm,
                                topMargin=15 * mm, bottomMargin=15 * mm)

        # Build the invoice
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        primary_color = colors.Color(*self.theme_colors["primary"])
        secondary_color = colors.Color(*self.theme_colors["secondary"])

        # Header with logo and store name
        logo_path = os.path.join(current_app.root_path, 'static', self.store_info['logo'].lstrip('/'))
        print(logo_path)
        header_data = []

        # Check if logo exists
        if os.path.exists(logo_path):
            logo_img = Image(logo_path)
            logo_img.drawHeight = 15 * mm
            logo_img.drawWidth = 40 * mm
            header_data = [[logo_img, ""]]
        else:
            # If no logo, use text
            header_data = [[
                Paragraph(f"<b>{self.store_info['name']}</b>",
                          ParagraphStyle('Logo', fontSize=16, textColor=primary_color)),
                ""
            ]]

        # Add invoice number centered
        header_data[0][1] = Paragraph(
            f"<b>Invoice # {self.invoice_number}</b>",
            ParagraphStyle('InvoiceNumber', fontSize=16, alignment=1)
        )

        header_table = Table(header_data, colWidths=[doc.width / 2, doc.width / 2])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 5 * mm))

        # Customer and store information
        # Create two columns for billing and shipping
        address_data = [
            [
                Paragraph("<b>BILL TO</b>",
                          ParagraphStyle('Header',
                                         fontSize=10,
                                         textColor=colors.white,
                                         backColor=primary_color,
                                         alignment=0,
                                         spaceBefore=5,
                                         spaceAfter=5,
                                         leftIndent=5)),
                Paragraph("<b>VENDOR</b>",
                          ParagraphStyle('Header',
                                         fontSize=10,
                                         textColor=colors.white,
                                         backColor=primary_color,
                                         alignment=0,
                                         spaceBefore=5,
                                         spaceAfter=5,
                                         leftIndent=5))
            ]
        ]

        # Customer information
        customer_info = [
            f"<b>{self.user.first_name} {self.user.last_name}</b>",
            f"{getattr(self.order.shipping_address, 'address', 'N/A')}",
            f"Invoice Date: {datetime.now().strftime('%m/%d/%Y')}",
            f"Due Date: {(datetime.now() + timedelta(days=14)).strftime('%m/%d/%Y')}"
        ]

        # Store information
        store_info = [
            f"<b>{self.store_info['name']}</b>",
            f"{self.store_info['address']}",
            f"Reg nr: {self.store_info['reg_number']}",
            f"TAX nr: {self.store_info['tax_number']}",
            f"Phone: {self.store_info['phone']}",
            ""
        ]

        # Add customer and store info to table
        address_data.append([
            Paragraph("<br />".join(customer_info), styles["Normal"]),
            Paragraph("<br />".join(store_info), styles["Normal"])
        ])

        address_table = Table(address_data, colWidths=[doc.width / 2 - 5 * mm, doc.width / 2 - 5 * mm])
        address_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('LEFTPADDING', (0, 0), (-1, 0), 5),
            ('RIGHTPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 0), (0, 0), primary_color),
            ('BACKGROUND', (1, 0), (1, 0), primary_color),
            ('BOX', (0, 0), (0, 1), 0.5, colors.black),
            ('BOX', (1, 0), (1, 1), 0.5, colors.black),
        ]))
        elements.append(address_table)
        elements.append(Spacer(1, 10 * mm))

        # Order items table
        items_header = [
            'DESCRIPTION', 'QTY', 'UNIT PRICE', 'SUBTOTAL', 'TAX'
        ]

        items_data = [items_header]

        # Calculate tax percentage
        tax_rate = float(self.store_info['tax_rate'])

        # Add items to table
        for item in self.order_details:
            product_name = item.product.name
            quantity = item.quantity
            unit_price = item.price
            subtotal = item.subtotal
            tax_amount = (subtotal * tax_rate / 100)

            # Check if this item has a discount
            discount_text = ""
            if hasattr(item, 'discount') and item.discount > 0:
                discount_text = f" (Discount {item.discount}%)"

            items_data.append([
                f"{product_name}{discount_text}",
                f"{quantity}",
                f"{self.store_info['currency_symbol']}{unit_price:.2f}",
                f"{self.store_info['currency_symbol']}{subtotal:.2f}",
                f"{self.store_info['currency_symbol']}{tax_amount:.2f} ({tax_rate}%)"
            ])

        # Add empty rows to make the table look more like the example
        for _ in range(3):
            items_data.append(["", "", "", "", ""])

        # Column widths
        col_widths = [doc.width * 0.4, doc.width * 0.1, doc.width * 0.15, doc.width * 0.15, doc.width * 0.2]

        # Create the items table
        items_table = Table(items_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 5 * mm))

        # Amount in words
        total_amount = self.order.total_amount
        amount_in_words = self.number_to_words(total_amount)

        words_para = Paragraph(
            f"<i>{amount_in_words}</i>",
            ParagraphStyle('Words', fontSize=10, leading=12)
        )
        elements.append(words_para)
        elements.append(Spacer(1, 5 * mm))

        # Summary calculations
        subtotal = sum(item.subtotal for item in self.order_details)
        tax_amount = subtotal * tax_rate / 100
        total = subtotal + tax_amount

        # Summary table
        summary_data = [
            ["", "", "SUBTOTAL", f"{self.store_info['currency_symbol']}{subtotal:.2f}"],
            ["", "", "TAX", f"{self.store_info['currency_symbol']}{tax_amount:.2f}"],
            ["", "", "Total", f"{self.store_info['currency_symbol']}{total:.2f}"]
        ]

        summary_table = Table(summary_data,
                              colWidths=[doc.width * 0.5, doc.width * 0.1, doc.width * 0.2, doc.width * 0.2])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (2, -1), (3, -1), primary_color),
            ('TEXTCOLOR', (2, -1), (3, -1), colors.white),
            ('LINEABOVE', (2, -1), (3, -1), 1, colors.black),
            ('GRID', (2, 0), (3, -1), 0.5, colors.black),
        ]))
        elements.append(summary_table)

        # Footer
        elements.append(Spacer(1, 10 * mm))

        footer_text = f"""
        <para align="center">
        <font size="8">
        Thank you for your business! | {self.store_info['name']} | {self.store_info['email']} | {self.store_info['phone']}
        </font>
        </para>
        """

        footer = Paragraph(footer_text, styles["Normal"])
        elements.append(footer)

        # Build the document
        doc.build(elements)

        # Get the PDF bytes and close the buffer
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def generate_html_receipt(self):
        """
        Generate an HTML version of the receipt for email or web viewing
        """
        if not self.fetch_order_data():
            return None

        # Get the total amount for the order
        total_amount = self.order.total_amount

        # Calculate tax amount
        tax_rate = float(self.store_info['tax_rate'])
        subtotal = sum(item.subtotal for item in self.order_details)
        tax_amount = subtotal * tax_rate / 100

        # Since we're using Flask, we can use render_template
        return render_template('ecommerce_invoice.html',
                               order=self.order,
                               user=self.user,
                               order_details=self.order_details,
                               store_info=self.store_info,
                               theme_colors=self.theme_colors,
                               invoice_number=self.invoice_number,
                               invoice_date=datetime.now().strftime('%m/%d/%Y'),
                               due_date=(datetime.now() + timedelta(days=14)).strftime('%m/%d/%Y'),
                               subtotal=subtotal,
                               tax_amount=tax_amount,
                               total_amount=total_amount,
                               amount_in_words=self.number_to_words(total_amount),
                               tax_rate=tax_rate)