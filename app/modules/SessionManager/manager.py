import uuid
import json
from app.extensions import redis_clients


class SessionManager:
    SESSION_DB = 0  # Redis DB 0 for session management
    SESSION_EXPIRY = 86400  # 1 Day Expiry (in seconds)

    @staticmethod
    def create_session(user_id):
        """Creates a new session and stores it in Redis."""
        session_id = str(uuid.uuid4())  # Generate unique session ID
        session_data = {"user_id": user_id}  # You can add more data if needed

        # Store session in Redis
        redis_clients[SessionManager.SESSION_DB].setex(
            f"session:{session_id}", SessionManager.SESSION_EXPIRY, json.dumps(session_data)
        )
        return session_id

    @staticmethod
    def get_session(session_id):
        """Retrieves session data from Redis."""
        session_data = redis_clients[SessionManager.SESSION_DB].get(f"session:{session_id}")
        return json.loads(session_data) if session_data else None

    @staticmethod
    def get_user_id_by_session_id(session_id):
        """Gets the user ID associated with a session ID."""
        session_data = SessionManager.get_session(session_id)
        return session_data["user_id"] if session_data else None

    @staticmethod
    def refresh_session(session_id):
        """Refreshes session expiry in Redis."""
        redis_clients[SessionManager.SESSION_DB].expire(f"session:{session_id}", SessionManager.SESSION_EXPIRY)

    @staticmethod
    def delete_session(session_id):
        """Deletes session from Redis."""
        redis_clients[SessionManager.SESSION_DB].delete(f"session:{session_id}")
