# app/modules/ProductManager.py
from app.models.models import Product, ProductCategory, ProductImage, FeaturedProduct
from app.extensions import db, minio_client
from sqlalchemy.exc import IntegrityError
import uuid

import os

MINIO_BUCKET = "sakuramart"


class ProductManager:
    @staticmethod
    def create_category(name, description=None, category_image=None):
        existing_category = ProductCategory.query.filter_by(name=name).first()
        if existing_category:
            return {"error": f"Category '{name}' already exists."}, 400

        new_category = ProductCategory(
            name=name,
            description=description,
            category_image=category_image
        )
        db.session.add(new_category)

        try:
            db.session.commit()
            return {"success": "Category created successfully!", "category_id": new_category.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Error creating category. Try again!"}, 500

    @staticmethod
    def create_product(name, description, category_id, price, stock_quantity, weight, tags=None, attributes=None,
                       images=None, is_featured=False, app=None):
        if price <= 0 or stock_quantity < 0 or weight <= 0:
            return {"error": "Invalid product data"}, 400

        category = ProductCategory.query.get(category_id)
        if not category:
            return {"error": "Invalid category ID"}, 404

        new_product = Product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            stock_quantity=stock_quantity,
            weight=weight,
            tags=tags or [],
            attributes=attributes or {},
            is_featured=is_featured
        )
        db.session.add(new_product)
        db.session.flush()

        image_urls = ProductManager.upload_images(new_product.id, images, app) if images else []  #pass the app to upload_images
        for image_url in image_urls:
            db.session.add(ProductImage(product_id=new_product.id, image_url=image_url))

        try:
            db.session.commit()
            return {"success": "Product created successfully!", "product_id": new_product.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Error creating product"}, 500

    @staticmethod
    def upload_images(product_id, image_files, app):
        uploaded_image_urls = []
        store_path = f"product/{product_id}/"

        if app:
            minio_client = app.extensions.get("minio_client")  #get the minio client.
        else:
            print("flask app not found")
            return []

        if minio_client:
            for image_file in image_files:
                if image_file and image_file.filename:
                    try:
                        image_name = f"{uuid.uuid4().hex}{os.path.splitext(image_file.filename)[1]}"
                        minio_path = f"{store_path}{image_name}"

                        minio_client.put_object(
                            bucket_name=MINIO_BUCKET,
                            object_name=minio_path,
                            data=image_file.stream,
                            length=-1,
                            part_size=10 * 1024 * 1024,
                            content_type=image_file.content_type or "image/jpeg"
                        )

                        image_url = f"https://cdn.sangonomiya.icu/{MINIO_BUCKET}/{minio_path}"
                        uploaded_image_urls.append(image_url)
                    except Exception as e:
                        print(f"Error uploading image: {str(e)}")
        else:
            print("Minio client not found")

        return uploaded_image_urls

    @staticmethod
    def get_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        return product.to_dict()

    @staticmethod
    def get_all_products():
        return [product.to_dict() for product in Product.query.all()]

    @staticmethod
    def get_featured_products():
        return [product.to_dict() for product in Product.query.join(FeaturedProduct).filter(
            FeaturedProduct.is_active).all()]

    @staticmethod
    def get_all_categories():
        return [category.to_dict() for category in ProductCategory.query.all()]

    @staticmethod
    def get_products_by_category(category_id):
        return [product.to_dict() for product in Product.query.filter_by(category_id=category_id).all()]

    @staticmethod
    def search_products(query):
        return [product.to_dict() for product in Product.query.filter(
            Product.name.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%")
        ).all()]

    @staticmethod
    def delete_product(product_id, app=None):
        """
        Delete a product and its associated images from the database and MinIO.

        Args:
            product_id (int): The ID of the product to delete.
            app (Flask): The Flask app instance to access the MinIO client.

        Returns:
            tuple: (response_dict, status_code)
        """
        # Fetch the product
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404

        # Get all associated images
        product_images = ProductImage.query.filter_by(product_id=product_id).all()
        image_urls = [img.image_url for img in product_images]

        # Extract MinIO object paths from image URLs
        if app:
            minio_client = app.extensions.get("minio_client")
        else:
            return {"error": "MinIO client not available"}, 500

        try:
            # Delete images from MinIO
            for image_url in image_urls:
                # Assuming URL format: https://cdn.sangonomiya.icu/sakuramart/product/<product_id>/<image_name>
                minio_path = image_url.replace(f"https://cdn.sangonomiya.icu/{MINIO_BUCKET}/", "")
                try:
                    minio_client.remove_object(
                        bucket_name=MINIO_BUCKET,
                        object_name=minio_path
                    )
                except Exception as e:
                    print(f"Error deleting MinIO object {minio_path}: {str(e)}")
                    # Continue with deletion even if one image fails (log the error)

            # Delete product and its images from the database
            # Delete associated ProductImage records
            ProductImage.query.filter_by(product_id=product_id).delete()
            # Delete from FeaturedProduct if applicable
            FeaturedProduct.query.filter_by(product_id=product_id).delete()
            # Delete the product itself
            db.session.delete(product)
            db.session.commit()

            return {"success": f"Product {product_id} and its images deleted successfully"}, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting product {product_id}: {str(e)}")
            return {"error": "Failed to delete product"}, 500