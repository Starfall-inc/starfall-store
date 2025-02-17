from app.models import db, Product, ProductCategory
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db # ✅ Import from extensions.py
from app.extensions import seraphina as logger # ✅ Import from extensions.py


class ProductManager:
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
            "reviews": [review.to_dict() for review in product.reviews],
            "stock_quantity": product.stock_quantity,
            "weight": float(product.weight),
            "images": [image.to_dict() for image in product.images],  # Convert images properly
            "tags": product.tags,
            "attributes": product.attributes,
            "is_featured": product.is_featured,
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
                "images": [image.to_dict() for image in product.images],  # Convert images properly
                "tags": product.tags,
                "is_featured": product.is_featured,
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
                "images": [image.to_dict() for image in product.images],  # Convert images properly
                "tags": product.tags,
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
                "images": [image.to_dict() for image in product.images],  # Convert images properly
                "tags": product.tags,
            }
            for product in products
        ]

    @staticmethod
    def get_product_by_id(product_id):
        product = Product.query.get_or_404(product_id)
        return product

    @staticmethod
    def get_latest_product():
        product = Product.query.order_by(Product.created_at.desc()).first()
        return product.to_dict() if product else None

    @staticmethod
    def search_products(query):
        if not query:
            return []

        search_term = f"%{query}%"
        products = Product.query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                db.cast(Product.attributes, db.String).ilike(search_term)
            )
        ).all()

        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "weight": float(product.weight),
                "images": [image.to_dict() for image in product.images],
                "tags": product.tags,
            }
            for product in products
        ]

    @classmethod
    def get_featured_products_by_category(cls, category_id):
        products = Product.query.filter(
            db.and_(
                Product.category_id == category_id,
                Product.is_featured == True
            )
        ).all()

        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "weight": float(product.weight),
                "images": [image.to_dict() for image in product.images],
                "tags": product.tags,
            }
            for product in products
        ]