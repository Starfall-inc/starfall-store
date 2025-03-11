from app.models.models import Banner

class PromotionManager:
    @staticmethod
    def get_active_promotions():
        # Query the database for active banners/promotions
        result = Banner.query.filter_by(active=True).all()
        return [promotion.to_dict() for promotion in result] if result else []

    @staticmethod
    def get_latest_promotion():
        # Get the latest banner (promotion) based on the created_at field
        result = Banner.query.order_by(Banner.created_at.desc()).first()
        if result:
            return result.to_dict()
        else:
            return None

    @staticmethod
    def get_promotion_by_id(promotion_id):
        # Get a specific promotion by its ID
        result = Banner.query.get(promotion_id)
        if result:
            return result.to_dict()
        else:
            return None

    @staticmethod
    def get_all_active_promotions():
        # Get all active promotions
        result = Banner.query.filter_by(active=True).all()
        return [promotion.to_dict() for promotion in result] if result else []

