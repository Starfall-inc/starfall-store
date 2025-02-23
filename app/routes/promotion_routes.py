from flask import Blueprint, request, jsonify
from app.extensions import db, seraphina, cache  # Assuming you have the cache object from Flask-Caching
from app.modules.PromotionManager import PromotionManager
from app.modules.ReviewManager import ReviewManager

promotion_bp = Blueprint("promotions", __name__)


@promotion_bp.route("/active", methods=["GET"])
def get_active_promotions():
    """Get all active promotions."""
    promotions = PromotionManager.get_active_promotions()
    seraphina.info("Fetched active promotions.")
    return jsonify(promotions)


@promotion_bp.route("/latest", methods=["GET"])
def get_latest_promotion():
    """Get the latest promotion."""
    promotion = PromotionManager.get_latest_promotion()
    seraphina.info("Fetched the latest promotion.")
    return jsonify(promotion)


@promotion_bp.route("/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
    """Get a specific promotion by ID."""
    promotion = PromotionManager.get_promotion_by_id(promotion_id)
    if not promotion:
        return jsonify({"error": "Promotion not found"}), 404
    seraphina.info(f"Fetched promotion {promotion_id}.")
    return jsonify(promotion)


@promotion_bp.route("/all", methods=["GET"])
def get_all_active_promotions():
    """Get all active promotions."""
    promotions = PromotionManager.get_all_active_promotions()
    seraphina.info("Fetched all active promotions.")
    return jsonify(promotions)
