from flask import Blueprint, request, jsonify, render_template, g
from app.extensions import db
from app.extensions import seraphina
from app.modules.ProductManager import ProductManager
from app.modules.ReviewManager import ReviewManager
from app.modules.PromotionManager import PromotionManager

staticroute_bp = Blueprint("siteroute", __name__)


@staticroute_bp.route('/')
def index():
    # Get promotions for slideshow
    promotions = PromotionManager.get_active_promotions()

    # Get featured products
    featured_products = ProductManager.get_featured_products()

    # Get all categories
    categories = ProductManager.get_all_categories()

    return render_template(
        'index.html',
        promotions=promotions,
        featured_products=featured_products,
        categories=categories
    )

@staticroute_bp.route('/about', methods=['GET'])
def render_about_page():
    return render_template('about.html')

@staticroute_bp.route('/orignal')
def index_orignal():
    features = [
        {"icon": "static/images/f1.png", "title": "Free Shipping"},
        {"icon": "static/images/f2.png", "title": "Save Time"},
        {"icon": "static/images/f3.png", "title": "Save Money"},
        {"icon": "static/images/f4.png", "title": "Promotions"},
        {"icon": "static/images/f5.png", "title": "Happy Sell"},
        {"icon": "static/images/f6.png", "title": "24/7 Support"}
    ]

    featured_products = [
        {
            "image": "static/images/p1.jpg",
            "brand": "adidas",
            "name": "Cartoon Astronaut T-shirt",
            "stars": 5,
            "price": 800
        }
        # Add more products as needed
    ]

    seraphina.info("Rendering index page")

    return render_template('index.html',
                           features=features,
                           featured_products=featured_products)


@staticroute_bp.route('/product/<int:product_id>', methods=['GET'])
def render_product_page(product_id):
    return render_template('product.html', product_id=product_id)


@staticroute_bp.route('/auth/signin', methods=['GET'])
def render_login_page():
    return render_template('auth/login.html')


@staticroute_bp.route('/auth/signup', methods=['GET'])
def render_signup_page():
    return render_template('auth/signup.html')


@staticroute_bp.route('/search', methods=['GET'])
def search():
    search_term = request.args.get("q", "").strip()  # Default to empty string
    category_id = request.args.get("category", "").strip()  # Default to empty string

    print(f"Search Query: {search_term}, Category ID: {category_id}")  # Debugging

    return render_template('search.html', query=search_term, category_id=category_id)



@staticroute_bp.route('/cart', methods=['GET'])
def render_cart_page():
    return render_template('cart.html')
