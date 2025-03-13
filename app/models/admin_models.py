from app.extensions import db
from datetime import datetime
import uuid


class Role(db.Model):
    """Role model for RBAC."""
    __tablename__ = "roles"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Role {self.name}>"


class RolePermission(db.Model):
    """Association table between roles and permissions."""
    __tablename__ = "role_permissions"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    role = db.relationship("Role", backref=db.backref("role_permissions", cascade="all, delete-orphan"))
    permission = db.relationship("Permissions", backref=db.backref("role_permissions", cascade="all, delete-orphan"))

    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),)

    def __repr__(self):
        return f"<RolePermission {self.role_id}:{self.permission_id}>"


class UserRole(db.Model):
    """Association table between users and roles."""
    __tablename__ = "user_roles"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    user = db.relationship("Users", foreign_keys=[user_id],
                           backref=db.backref("user_roles", cascade="all, delete-orphan"))
    role = db.relationship("Role", backref=db.backref("user_roles", cascade="all, delete-orphan"))
    creator = db.relationship("Users", foreign_keys=[created_by])

    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),)

    def __repr__(self):
        return f"<UserRole {self.user_id}:{self.role_id}>"


# Update existing Permissions model to improve it for RBAC
class Permissions(db.Model):
    """Permissions model."""
    __tablename__ = "permissions"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    group = db.Column(db.String(255), nullable=False)
    actions = db.Column(db.String(255), default="")  # Store as comma-separated string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Permission {self.name}>"

    @property
    def action_list(self):
        """Convert the comma-separated actions string to a list."""
        return self.actions.split(',') if self.actions else []


# Update Users model with RBAC helper methods
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

    def __repr__(self):
        return f"<AdminUser {self.email}>"

    @property
    def roles(self):
        """Return a list of roles assigned to the user."""
        return [user_role.role for user_role in self.user_roles]

    @property
    def role_names(self):
        """Return a list of role names assigned to the user."""
        return [role.name for role in self.roles]

    def has_role(self, role_name):
        """Check if user has the specified role."""
        return role_name in self.role_names

    def has_permission(self, permission_name, action=None):
        """Check if user has the specified permission and optional action."""
        for role in self.roles:
            for role_perm in role.role_permissions:
                if role_perm.permission.name == permission_name:
                    # If no specific action required, or action is in the permission's actions
                    if action is None or action in role_perm.permission.action_list:
                        return True
        return False

    def add_role(self, role, created_by=None):
        """Add a role to the user."""
        if isinstance(role, str):
            # If a string is provided, find the role by name
            role = Role.query.filter_by(name=role).first()
            if not role:
                return False

        # Check if the user already has the role
        if not any(ur.role_id == role.id for ur in self.user_roles):
            user_role = UserRole(user_id=self.id, role_id=role.id, created_by=created_by)
            db.session.add(user_role)
            return True
        return False

    def remove_role(self, role):
        """Remove a role from the user."""
        if isinstance(role, str):
            # If a string is provided, find the role by name
            role = Role.query.filter_by(name=role).first()
            if not role:
                return False

        user_role = UserRole.query.filter_by(user_id=self.id, role_id=role.id).first()
        if user_role:
            db.session.delete(user_role)
            return True
        return False


class AdminLogs(db.Model):
    """Logs admin actions for accountability."""
    __tablename__ = "admin_logs"
    __bind_key__ = "admin_db"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.JSON, nullable=True)  # Store extra metadata (order ID, product name, etc.)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    admin = db.relationship("Users", backref=db.backref("logs", lazy="dynamic"))

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