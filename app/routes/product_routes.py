from flask import Blueprint, request, jsonify
from app.extensions import db, seraphina, cache  # Assuming you have the cache object from Flask-Caching
from app.modules.ProductManager import ProductManager
from app.modules.ReviewManager import ReviewManager

product_bp = Blueprint("product", __name__)


# 🟢 Get all products
@product_bp.route("/", methods=["GET"])
def get_products():
    cache_key = "all_products"
    cached_products = cache.get(cache_key)

    if cached_products:
        seraphina.info("Fetched products from cache.")
        return jsonify(cached_products)

    # If not in cache, fetch normally and cache it
    products = ProductManager.get_all_products()
    products_dict = [product for product in products]
    cache.set(cache_key, products_dict, timeout=60 * 60)  # Cache for 1 hour

    seraphina.info("Fetched products normally and cached the result.")
    return jsonify(products_dict)


# 🟢 Get a single product by ID
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    cache_key = f"product_{product_id}"
    cached_product = cache.get(cache_key)

    if cached_product:
        seraphina.info(f"Fetched product {product_id} from cache.")
        return jsonify(cached_product)

    # If not in cache, fetch normally and cache it
    product = ProductManager.get_product(product_id)
    product_dict = product
    cache.set(cache_key, product_dict, timeout=60 * 60)  # Cache for 1 hour

    seraphina.info(f"Fetched product {product_id} normally and cached the result.")
    return jsonify(product_dict)


# 🟢 Get featured products
@product_bp.route("/featured", methods=["GET"])
def get_featured_products():
    cache_key = "featured_products"
    cached_featured = cache.get(cache_key)

    if cached_featured:
        seraphina.info("Fetched featured products from cache.")
        return jsonify(cached_featured)

    # If not in cache, fetch normally and cache it
    products = ProductManager.get_featured_products()
    featured_products_dict = [product for product in products]
    cache.set(cache_key, featured_products_dict, timeout=60 * 60)  # Cache for 1 hour

    seraphina.info("Fetched featured products normally and cached the result.")
    return jsonify(featured_products_dict)


# 🟢 Get all product categories
@product_bp.route("/categories", methods=["GET"])
def get_product_categories():
    cache_key = "product_categories"
    cached_categories = cache.get(cache_key)

    if cached_categories:
        seraphina.info("Fetched product categories from cache.")
        return jsonify(cached_categories)

    # If not in cache, fetch normally and cache it
    categories = ProductManager.get_all_categories()
    categories_dict = [category for category in categories]
    cache.set(cache_key, categories_dict, timeout=60 * 60)

    seraphina.info("Fetched product categories normally and cached the result.")
    return jsonify(categories_dict)

