from flask import Blueprint, request, jsonify, render_template, g, flash, redirect, url_for
from flask import render_template
from app.models.models import User, Order, Product, ProductCategory
from app.extensions import db

admin_static_routes_bp = Blueprint("admin_static", __name__)


@admin_static_routes_bp.route("/")
def admin_dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status="pending").count()
    completed_orders = Order.query.filter_by(status="paid").count()
    total_revenue = db.session.query(db.func.sum(Order.total)).filter_by(status="Paid").scalar() or 0
    total_products = Product.query.count()
    total_categories = ProductCategory.query.count()
    recent_orders = Order.query.order_by(Order.order_place_date.desc()).limit(5).all()
    recent_users = User.query.order_by(User.joined_at.desc()).limit(5).all()

    return render_template(
        "admin/index.html",
        total_users=total_users,
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        total_revenue=total_revenue,
        total_products=total_products,
        total_categories=total_categories,
        recent_orders=recent_orders,
        recent_users=recent_users
    )


@admin_static_routes_bp.route("/products", methods=["GET"])
def manage_products():
    """
    Renders the product management dashboard with all products & categories.
    """
    products = Product.query.all()  # Fetch all products
    categories = ProductCategory.query.all()  # Fetch all categories

    # Convert products to a list of dictionaries
    product_list = [product.to_dict() for product in products]
    category_list = [category.to_dict() for category in categories]

    return render_template("admin/product/main.html", products=product_list, categories=category_list)


@admin_static_routes_bp.route("/product/add", methods=["POST"])
def add_product():
    """
    Adds a new product to the database.
    """
    try:
        name = request.form.get("name")
        description = request.form.get("description")
        category_id = request.form.get("category_id")
        price = float(request.form.get("price"))
        stock_quantity = int(request.form.get("stock_quantity"))
        is_featured = bool(request.form.get("is_featured"))

        new_product = Product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            stock_quantity=stock_quantity,
            is_featured=is_featured,
        )

        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin.manage_products"))


@admin_static_routes_bp.route("/product/delete/<int:product_id>", methods=["GET"])
def delete_product(product_id):
    """
    Deletes a product from the database.
    """
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("admin_static.manage_products"))


@admin_static_routes_bp.route("/product/edit/<int:product_id>", methods=["POST"])
def edit_product(product_id):
    """
    Edits an existing product.
    """
    try:
        product = Product.query.get_or_404(product_id)
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.category_id = request.form.get("category_id")
        product.price = float(request.form.get("price"))
        product.stock_quantity = int(request.form.get("stock_quantity"))
        product.is_featured = bool(request.form.get("is_featured"))

        db.session.commit()
        flash("Product updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating product: {str(e)}", "danger")

    return redirect(url_for("admin.manage_products"))


@admin_static_routes_bp.route("/categories", methods=["POST"])
def add_category():
    """
    Adds a new product category.
    """
    try:
        name = request.form.get("name")
        description = request.form.get("description")

        category = ProductCategory(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for("admin.manage_products"))


# --------- Order Static Page Routes --------- #

@admin_static_routes_bp.route("/orders", methods=["GET"])
def manage_orders():
    """
    Renders the order management dashboard with all orders.
    """
    return render_template("admin/orders/main.html")

@admin_static_routes_bp.route("/store/settings", methods=["GET"])
def render_settings_page():
    return render_template("admin/store/settings.html")