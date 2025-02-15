from app.extensions import redis_clients

class RedisManager:
    @staticmethod
    def set_data(db_index, key, value, expiry=None):
        """Stores data in the specified Redis database index."""
        redis_clients[db_index].setex(key, expiry or 86400, value)

    @staticmethod
    def get_data(db_index, key):
        """Retrieves data from the specified Redis database index."""
        return redis_clients[db_index].get(key)

    @staticmethod
    def delete_data(db_index, key):
        """Deletes data from the specified Redis database index."""
        redis_clients[db_index].delete(key)
