from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import uuid

class Roles(db.Model):
    """Admin role model."""
    __tablename__ = "roles"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)  # Role description

    # Relationships
    users = db.relationship("Users", secondary="user_roles", back_populates="roles")
    permissions = db.relationship("Permissions", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<AdminRole {self.name}>"

class Permissions(db.Model):
    """Permissions model."""
    __tablename__ = "permissions"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    group = db.Column(db.String(255), nullable=False)  # User Management, Order Management, etc.
    actions = db.Column(ARRAY(db.String(255)), default=[])  # ["view", "edit", "delete"]

    # Relationships
    roles = db.relationship("Roles", secondary="role_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"

class Users(db.Model):
    """Admin user model."""
    __tablename__ = "users"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="active")  # active, suspended, banned
    login_attempts = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = db.relationship("Roles", secondary="user_roles", back_populates="users")
    logs = db.relationship("AdminLogs", back_populates="admin")

    def __repr__(self):
        return f"<AdminUser {self.email}>"

class AdminLogs(db.Model):
    """Logs admin actions for accountability."""
    __tablename__ = "admin_logs"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(JSONB, nullable=True)  # Store extra metadata (order ID, product name, etc.)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    admin = db.relationship("Users", back_populates="logs")

    def __repr__(self):
        return f"<AdminLog {self.admin_id} - {self.action}>"

class Settings(db.Model):
    """Stores global admin settings."""
    __tablename__ = "settings"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Setting {self.key}>"
