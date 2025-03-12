from app import db
from app.models.models import Banner

class PromotionManager:
    @staticmethod
    def create_promotion(title, description, image_url, discount_percent, start_date=None, end_date=None):
        """Creates a new promotion."""
        try:
            promotion = Banner(
                title=title,
                description=description,
                image_url=image_url,
                discount_percent=discount_percent,
                start_date=start_date,
                end_date=end_date,
                active=True  # Default to active
            )
            db.session.add(promotion)
            db.session.commit()
            return {"success": True, "message": "Promotion created successfully.", "promotion_id": promotion.id}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_promotion(promotion_id, title=None, description=None, image_url=None, discount_percent=None, start_date=None, end_date=None, active=None):
        """Updates an existing promotion."""
        try:
            promotion = Banner.query.get(promotion_id)
            if not promotion:
                return {"success": False, "error": "Promotion not found."}

            if title is not None:
                promotion.title = title
            if description is not None:
                promotion.description = description
            if image_url is not None:
                promotion.image_url = image_url
            if discount_percent is not None:
                promotion.discount_percent = discount_percent
            if start_date is not None:
                promotion.start_date = start_date
            if end_date is not None:
                promotion.end_date = end_date
            if active is not None:
                promotion.active = active

            db.session.commit()
            return {"success": True, "message": "Promotion updated successfully."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def toggle_promotion_status(promotion_id, status):
        """Activates or deactivates a promotion."""
        promotion = Banner.query.get(promotion_id)
        if not promotion:
            return {"success": False, "error": "Promotion not found."}

        promotion.active = status
        db.session.commit()
        return {"success": True, "message": f"Promotion {'activated' if status else 'deactivated'} successfully."}


    @staticmethod
    def delete_promotion(promotion_id):
        """Deletes a promotion."""
        try:
            promotion = Banner.query.get(promotion_id)
            if not promotion:
                return {"success": False, "error": "Promotion not found."}

            db.session.delete(promotion)
            db.session.commit()
            return {"success": True, "message": "Promotion deleted successfully."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}


    @staticmethod
    def get_promotions(filters=None):
        """Fetch promotions with optional filters."""
        query = Banner.query

        if filters:
            if "status" in filters:
                query = query.filter_by(active=filters["status"])
            if "date_range" in filters:
                start_date, end_date = filters["date_range"]
                query = query.filter(Banner.start_date.between(start_date, end_date))

        promotions = query.order_by(Banner.created_at.desc()).all()

        return [
            {
                "promotion_id": promo.id,
                "title": promo.title,
                "description": promo.description,
                "image_url": promo.image_url,
                "discount_percent": promo.discount_percent,
                "start_date": promo.start_date,
                "end_date": promo.end_date,
                "status": "Active" if promo.active else "Inactive"
            }
            for promo in promotions
        ]
