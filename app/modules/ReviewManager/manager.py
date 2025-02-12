from sqlalchemy.exc import SQLAlchemyError

from app.models import Product
from app.models import ProductReview as Review
from app.extensions import db, logger

class ReviewManager:
    @staticmethod
    def add_review(product_id, user_id, rating, review):
        try:
            review = Review(
                product_id=product_id,
                user_id=user_id,
                rating=rating,
                review=review
            )
            db.session.add(review)
            db.session.commit()
            return {"message": "Review added successfully", "review_id": review.id}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def update_review(review_id, **kwargs):
        try:
            review = Review.query.get(review_id)
            if not review:
                return {"error": "Review not found"}

            for key, value in kwargs.items():
                if hasattr(review, key):
                    setattr(review, key, value)

            db.session.commit()
            return {"message": "Review updated successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def delete_review(review_id):
        try:
            review = Review.query.get(review_id)
            if not review:
                return {"error": "Review not found"}

            db.session.delete(review)
            db.session.commit()
            return {"message": "Review deleted successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def get_reviews(product_id):
        reviews = Review.query.filter_by(product_id=product_id).all()
        return reviews