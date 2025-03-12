from app.models.models import Product, ProductCategory
from app.extensions import db  # ✅ Import from extensions.py
from sqlalchemy.exc import IntegrityError


class ProductManager:
    @staticmethod
    def create_category(name, description=None, category_image=None):
        """
        Creates a new product category.
        """
        # Check if category already exists
        existing_category = ProductCategory.query.filter_by(name=name).first()
        if existing_category:
            return {"error": f"Category '{name}' already exists."}, 400

        # Create and add the new category
        new_category = ProductCategory(name=name, description=description, category_image=category_image)
        db.session.add(new_category)

        try:
            db.session.commit()
            return {"success": "Category created successfully!", "category_id": new_category.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Error creating category. Try again!"}, 500

    @staticmethod
    def create_product(name, description, category_id, price, stock_quantity, weight, tags=None, attributes=None,
                       images=None, is_featured=False):
        """
        Creates a new product with proper validation and error handling.
        """
        # Validate price, stock, and weight
        if price <= 0 or stock_quantity < 0 or weight <= 0:
            return {"error": "Invalid product data. Price, weight must be positive, stock must be non-negative."}, 400

        # Check if category exists
        category = ProductCategory.query.get(category_id)
        if not category:
            return {"error": "Invalid category ID. Category not found."}, 404

        # Convert images to JSON format
        formatted_images = [img.to_dict() for img in images] if images else []

        # Create and add new product
        new_product = Product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            stock_quantity=stock_quantity,
            weight=weight,
            tags=tags or [],
            attributes=attributes or {},
            images=formatted_images,
            is_featured=is_featured
        )
        db.session.add(new_product)

        try:
            db.session.commit()
            return {"success": "Product created successfully!", "product_id": new_product.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Error creating product. Try again!"}, 500

    @staticmethod
    def bulk_create_products(products_data):
        """
        Bulk create multiple products in a single transaction.
        """
        created_products = []
        failed_products = []

        for product in products_data:
            result, status_code = ProductManager.create_product(
                name=product.get("name"),
                description=product.get("description"),
                category_id=product.get("category_id"),
                price=product.get("price"),
                stock_quantity=product.get("stock_quantity"),
                weight=product.get("weight"),
                tags=product.get("tags"),
                attributes=product.get("attributes"),
                images=product.get("images"),
                is_featured=product.get("is_featured", False)
            )

            if status_code == 201:
                created_products.append(result)
            else:
                failed_products.append({"product": product.get("name"), "error": result["error"]})

        return {"created": created_products, "failed": failed_products}
