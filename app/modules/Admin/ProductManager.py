from app.models.models import Product, ProductCategory, ProductImage
from app.extensions import db, minio_client
from sqlalchemy.exc import IntegrityError
import uuid
import os

# Configure your MinIO bucket
MINIO_BUCKET = "sakuramart"

class ProductManager:
    @staticmethod
    def create_category(name, description=None, category_image=None):
        """
        Creates a new product category.
        """
        existing_category = ProductCategory.query.filter_by(name=name).first()
        if existing_category:
            return {"error": f"Category '{name}' already exists."}, 400

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
        Creates a new product and uploads images to MinIO.
        """
        if price <= 0 or stock_quantity < 0 or weight <= 0:
            return {"error": "Invalid product data. Price, weight must be positive, stock must be non-negative."}, 400

        category = ProductCategory.query.get(category_id)
        if not category:
            return {"error": "Invalid category ID. Category not found."}, 404

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
        db.session.flush()  # Get product_id before committing

        # ✅ Upload images to MinIO
        image_urls = ProductManager.upload_images(new_product.id, images) if images else []

        # ✅ Store image URLs in `ProductImage` table
        for image_url in image_urls:
            db.session.add(ProductImage(product_id=new_product.id, image_url=image_url))

        try:
            db.session.commit()
            return {"success": "Product created successfully!", "product_id": new_product.id}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Error creating product. Try again!"}, 500

    @staticmethod
    def upload_images(product_id, image_files):
        """
        Uploads images to MinIO and returns the URLs.
        """
        uploaded_image_urls = []
        store_path = f"{MINIO_BUCKET}/product/{product_id}/"

        for image_file in image_files:
            try:
                image_name = f"{uuid.uuid4().hex}{os.path.splitext(image_file.filename)[1]}"
                minio_path = f"{store_path}{image_name}"

                # ✅ Upload to MinIO
                minio_client.put_object(
                    bucket_name=MINIO_BUCKET,
                    object_name=minio_path,
                    data=image_file.stream,
                    length=-1,
                    part_size=10 * 1024 * 1024,  # 10MB Chunk Size
                    content_type=image_file.content_type
                )

                # ✅ Generate public URL
                image_url = f"https://cdn.sangonomiya.icu/{minio_path}"
                uploaded_image_urls.append(image_url)
            except Exception as e:
                print(f"Error uploading image: {str(e)}")

        return uploaded_image_urls

    @staticmethod
    def get_product(product_id):
        """
        Fetches a product by ID with all its images.
        """
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
            "images": [image.to_dict() for image in product.images],  # ✅ Fetch from ProductImage table
            "tags": product.tags,
            "attributes": product.attributes,
            "is_featured": product.is_featured,
            "avg_rating": product.average_rating,
        }
