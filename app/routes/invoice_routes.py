# invoice Routes
from flask import Blueprint, send_file, abort, make_response
from io import BytesIO
from app.models.models import Order
from app.modules.InvoiceManager.manager import EcommerceInvoiceGenerator as ReceiptGenerator

receipt_bp = Blueprint('receipt', __name__, url_prefix='/receipts')


@receipt_bp.route('/<int:order_id>')
def get_receipt(order_id):
    """
    Generate and return a PDF receipt for direct download

    Args:
        order_id (int): The ID of the order

    Returns:
        Flask Response: PDF file download
    """
    # Check if order exists
    order = Order.query.get_or_404(order_id)

    # Generate the receipt
    receipt_generator = ReceiptGenerator(order_id)
    pdf_bytes = receipt_generator.generate_pdf_bytes()

    if not pdf_bytes:
        abort(500, "Failed to generate receipt")

    # Create buffer with PDF bytes
    pdf_buffer = BytesIO(pdf_bytes)

    # Generate filename
    filename = f"invoice_order_{order_id}.pdf"

    # Return the PDF as a downloadable file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )