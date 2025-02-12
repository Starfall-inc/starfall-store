from flask import Blueprint, request, jsonify, render_template
from app.extensions import db,logger
from app.modules.ProductManager import ProductManager
from app.modules.ReviewManager import ReviewManager



staticroute_bp = Blueprint("siteroute", __name__)


@staticroute_bp.route('/')
def index():
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

    return render_template('index.html',
                           features=features,
                           featured_products=featured_products)