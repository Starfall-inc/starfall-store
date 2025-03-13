import uuid
import json
from app.extensions import redis_clients

class AdminSessionManager:
    ADMIN_SESSION_DB = 1  # Redis DB 1 for admin sessions
    ADMIN_SESSION_EXPIRY = 86400  # 1 Day Expiry (in seconds)

    @staticmethod
    def create_session(admin_id):
        """Creates a new admin session and stores it in Redis."""
        session_id = str(uuid.uuid4())  # Generate unique session ID
        session_data = {"admin_id": admin_id}  # Store admin ID

        redis_clients[AdminSessionManager.ADMIN_SESSION_DB].setex(
            f"admin_session:{session_id}", AdminSessionManager.ADMIN_SESSION_EXPIRY, json.dumps(session_data)
        )
        return session_id

    @staticmethod
    def get_session(session_id):
        """Retrieves admin session data from Redis."""
        session_data = redis_clients[AdminSessionManager.ADMIN_SESSION_DB].get(f"admin_session:{session_id}")
        return json.loads(session_data) if session_data else None

    @staticmethod
    def get_admin_id_by_session_id(session_id):
        """Gets the admin ID associated with a session ID."""
        session_data = AdminSessionManager.get_session(session_id)
        return session_data["admin_id"] if session_data else None

    @staticmethod
    def refresh_session(session_id):
        """Refreshes session expiry in Redis."""
        redis_clients[AdminSessionManager.ADMIN_SESSION_DB].expire(f"admin_session:{session_id}", AdminSessionManager.ADMIN_SESSION_EXPIRY)

    @staticmethod
    def delete_session(session_id):
        """Deletes session from Redis."""
        redis_clients[AdminSessionManager.ADMIN_SESSION_DB].delete(f"admin_session:{session_id}")
