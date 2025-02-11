from app.models import db, Product, ProductCategory
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db, logger # ✅ Import from extensions.py


class ProductManager:
    @staticmethod
    def add_product(name, description, category_id, price, stock_quantity, weight, image_url=None, tags=None):
        try:
            product = Product(
                name=name,
                description=description,
                category_id=category_id,
                price=price,
                stock_quantity=stock_quantity,
                weight=weight,
                image_url=image_url,
                tags=tags
            )
            db.session.add(product)
            db.session.commit()
            return {"message": "Product added successfully", "product_id": product.id}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def update_product(product_id, **kwargs):
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"error": "Product not found"}

            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            db.session.commit()
            return {"message": "Product updated successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def delete_product(product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"error": "Product not found"}

            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def get_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}

        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category_id": product.category_id,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "weight": float(product.weight),
            "image_url": product.image_url,
            "tags": product.tags,
            "created_at": product.created_at
        }

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category_id": product.category_id,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "weight": float(product.weight),
                "image_url": product.image_url,
                "tags": product.tags,
                "created_at": product.created_at
            }
            for product in products
        ]

    @staticmethod
    def get_products_by_category(category_id):
        products = Product.query.filter_by(category_id=category_id).all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "weight": float(product.weight),
                "image_url": product.image_url,
                "tags": product.tags,
                "created_at": product.created_at
            }
            for product in products
        ]

    @staticmethod
    def get_featured_products():
        products = Product.query.filter_by(is_featured=True).all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "weight": float(product.weight),
                "image_url": product.image_url,
                "tags": product.tags,
                "created_at": product.created_at
            }
            for product in products
        ]

    @staticmethod
    def get_product_by_id(product_id):
        product = Product.query.get_or_404(product_id)
        return product
