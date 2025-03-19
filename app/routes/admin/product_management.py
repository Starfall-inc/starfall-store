# app/api/product_api.py
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, render_template
from app.extensions import db, seraphina, cache
from app.modules.Admin.ProductManager import ProductManager
from app.models.models import Product, ProductCategory, ProductImage, FeaturedProduct
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os
import csv
from io import StringIO
import json

product_bp = Blueprint("product_api", __name__)


# Helper function to clear relevant cache
def clear_cache(pattern):
    if isinstance(pattern, list):
        for p in pattern:
            cache.delete(p)
    else:
        cache.delete(pattern)


# Route to render the admin page with data
@product_bp.route("/admin/products", methods=["GET"])
def admin_products_page():
    products = Product.query.all()
    products_json = [product.to_dict() for product in products]
    categories = ProductCategory.query.all()

    return render_template(
        "admin/products.html",
        products=products_json,
        categories=categories
    )


# API: Get all products (Admin view)
@product_bp.route("/api/admin/products/", methods=["GET"])
def get_products():
    cache_key = "admin_all_products"
    cached_products = cache.get(cache_key)

    if cached_products:
        seraphina.info("Fetched products from cache for admin.")
        return jsonify(cached_products)

    # Add pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    products_dict = [product.to_dict() for product in products]

    # Add pagination metadata
    result = {
        "products": products_dict,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }

    cache.set(cache_key, result, timeout=60 * 5)  # Cache for 5 minutes
    return jsonify(result)


# API: Create a new product
@product_bp.route("/api/admin/products/", methods=["POST"])
def create_product():
    if not request.form or 'name' not in request.form:
        return jsonify({"error": "Missing required fields"}), 400

    data = request.form
    image_files = request.files.getlist("images")

    # Validate required fields
    try:
        price = float(data.get("price", 0))
        stock_quantity = int(data.get("stock_quantity", 0))
        weight = float(data.get("weight", 0))
        category_id = int(data.get("category_id", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid numeric values"}), 400

    tags = data.get("tags", "").split(",") if data.get("tags") else []
    is_featured = data.get("is_featured") == "on"

    try:
        result, status = ProductManager.create_product(
            name=data.get("name"),
            description=data.get("description", ""),
            category_id=category_id,
            price=price,
            stock_quantity=stock_quantity,
            weight=weight,
            tags=[tag.strip() for tag in tags],
            images=image_files,
            is_featured=is_featured
        )

        if status == 201 and is_featured:
            # Add to FeaturedProduct table
            featured = FeaturedProduct(
                product_id=result["product_id"],
                from_date=db.func.now(),
                to_date=db.func.now() + db.text("INTERVAL '30 days'")
            )
            db.session.add(featured)
            db.session.commit()

        # Clear relevant caches
        clear_cache(["admin_all_products", "featured_products"])

        # Redirect with success message
        return redirect(url_for('product_api.admin_products_page') + "?message=Product added successfully&type=success")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error creating product: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') + "?message=Failed to add product&type=error")


# API: Get product details for edit
@product_bp.route("/admin/product/<int:product_id>", methods=["GET"])
def get_product_details(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        seraphina.error(f"Error fetching product details: {str(e)}")
        return jsonify({"error": "Product not found"}), 404


# API: Update product
@product_bp.route("/admin/product/update", methods=["POST"])
def update_product():
    data = request.form
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    try:
        product = Product.query.get_or_404(product_id)

        if "name" in data:
            product.name = data["name"]
        if "price" in data:
            product.price = float(data["price"])
        if "stock_quantity" in data:
            product.stock_quantity = int(data["stock_quantity"])

        # Handle image update
        if "image" in request.files and request.files["image"].filename:
            image_file = request.files["image"]
            image_urls = ProductManager.upload_images(product.id, [image_file])
            if image_urls:
                # Update first image or add new one
                if product.images:
                    product.images[0].image_url = image_urls[0]
                else:
                    db.session.add(ProductImage(product_id=product.id, image_url=image_urls[0]))

        db.session.commit()

        # Clear caches
        clear_cache([f"product_{product_id}", "admin_all_products"])

        return redirect(
            url_for('product_api.admin_products_page') + "?message=Product updated successfully&type=success")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error updating product: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') + "?message=Failed to update product&type=error")


# API: Delete product
@product_bp.route("/admin/product/delete/<int:product_id>", methods=["GET"])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()

        # Clear caches
        clear_cache([f"product_{product_id}", "admin_all_products", "featured_products"])

        return redirect(
            url_for('product_api.admin_products_page') + "?message=Product deleted successfully&type=success")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error deleting product: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') + "?message=Failed to delete product&type=error")


# API: Bulk upload products
@product_bp.route("/admin/products/bulk-upload", methods=["POST"])
def bulk_upload_products():
    if "csv_file" not in request.files:
        return redirect(url_for('product_api.admin_products_page') + "?message=No CSV file provided&type=error")

    csv_file = request.files["csv_file"]
    if not csv_file.filename.endswith('.csv'):
        return redirect(url_for('product_api.admin_products_page') + "?message=File must be a CSV&type=error")

    try:
        csv_data = csv_file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_data))
        success_count = 0

        for row in csv_reader:
            try:
                result, status = ProductManager.create_product(
                    name=row["name"],
                    description=row.get("description", ""),
                    category_id=int(row["category_id"]),
                    price=float(row["price"]),
                    stock_quantity=int(row["stock_quantity"]),
                    weight=float(row.get("weight", "1.0")),
                    tags=row.get("tags", "").split(",") if row.get("tags") else []
                )
                if status == 201:
                    success_count += 1
            except Exception as e:
                seraphina.error(f"Error processing row in bulk upload: {str(e)}")
                continue

        # Clear cache
        clear_cache("admin_all_products")

        return redirect(url_for('product_api.admin_products_page') +
                        f"?message=Bulk upload completed. {success_count} products added.&type=success")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error in bulk upload: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') + "?message=Bulk upload failed&type=error")


# API: Sample CSV download
@product_bp.route("/admin/products/sample-csv", methods=["GET"])
def download_sample_csv():
    try:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "category_id", "price", "stock_quantity", "weight", "tags", "description"])
        writer.writerow(["Sample Product", "1", "999.99", "10", "0.5", "tag1,tag2", "Sample description"])

        return current_app.response_class(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=sample_products.csv"}
        )
    except Exception as e:
        seraphina.error(f"Error generating sample CSV: {str(e)}")
        return jsonify({"error": "Failed to generate sample CSV"}), 500


# API: Category management routes
@product_bp.route("/admin/category/add", methods=["POST"])
def add_category():
    try:
        data = request.form
        result, status = ProductManager.create_category(
            name=data.get("name"),
            description=data.get("description", "")
        )

        if status == 201:
            clear_cache("product_categories")
            return redirect(url_for('product_api.admin_products_page') +
                            "?message=Category added successfully&type=success")
        else:
            return redirect(url_for('product_api.admin_products_page') +
                            f"?message={result.get('error', 'Failed to add category')}&type=error")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error adding category: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') + "?message=Failed to add category&type=error")


@product_bp.route("/admin/category/edit/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    category = ProductCategory.query.get_or_404(category_id)

    if request.method == "GET":
        # Render edit form
        return render_template("admin/edit_category.html", category=category)

    if request.method == "POST":
        try:
            data = request.form

            if "name" in data:
                category.name = data["name"]
            if "description" in data:
                category.description = data["description"]

            db.session.commit()
            clear_cache("product_categories")

            return redirect(url_for('product_api.admin_products_page') +
                            "?message=Category updated successfully&type=success")

        except IntegrityError:
            db.session.rollback()
            return redirect(url_for('product_api.admin_products_page') +
                            "?message=Category name already exists&type=error")
        except Exception as e:
            db.session.rollback()
            seraphina.error(f"Error updating category: {str(e)}")
            return redirect(url_for('product_api.admin_products_page') +
                            "?message=Failed to update category&type=error")


@product_bp.route("/admin/category/delete/<int:category_id>", methods=["GET"])
def delete_category(category_id):
    try:
        category = ProductCategory.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()

        clear_cache("product_categories")

        return redirect(url_for('product_api.admin_products_page') +
                        "?message=Category deleted successfully&type=success")

    except Exception as e:
        db.session.rollback()
        seraphina.error(f"Error deleting category: {str(e)}")
        return redirect(url_for('product_api.admin_products_page') +
                        "?message=Failed to delete category&type=error")


# API: Get product categories for select boxes
@product_bp.route("/api/admin/categories", methods=["GET"])
def get_categories():
    cache_key = "product_categories"
    cached_categories = cache.get(cache_key)

    if cached_categories:
        return jsonify(cached_categories)

    categories = ProductCategory.query.all()
    categories_dict = [category.to_dict() for category in categories]

    cache.set(cache_key, categories_dict, timeout=60 * 60)  # Cache for an hour

    return jsonify(categories_dict)


# API: Handle pagination
@product_bp.route("/api/admin/products/page/<int:page>", methods=["GET"])
def paginate_products(page):
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    products_dict = [product.to_dict() for product in products]

    result = {
        "products": products_dict,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }

    return jsonify(result)