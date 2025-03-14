from app.extensions import db
from app.models.admin_models import Users, Role, Permissions, UserRole, RolePermission
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import Seraphina as logger


class RBACManager:
    """
    Role-Based Access Control (RBAC) Manager
    Handles roles, permissions, and user role assignments securely.
    """

    # ✅ Create a new role
    @staticmethod
    def create_role(name, description=""):
        try:
            if Role.query.filter_by(name=name).first():
                return {"error": "Role already exists"}, 400

            new_role = Role(name=name, description=description)
            db.session.add(new_role)
            db.session.commit()
            return {"success": f"Role '{name}' created successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating role: {e}")
            return {"error": "Internal server error"}, 500

    # ✅ Create a new permission
    @staticmethod
    def create_permission(name, group, actions=None):
        try:
            if Permissions.query.filter_by(name=name).first():
                return {"error": "Permission already exists"}, 400

            actions_str = ",".join(actions) if actions else ""  # Store actions as comma-separated string
            new_permission = Permissions(name=name, group=group, actions=actions_str)
            db.session.add(new_permission)
            db.session.commit()
            return {"success": f"Permission '{name}' created successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating permission: {e}")
            return {"error": "Internal server error"}, 500

    # ✅ Assign permissions to a role
    @staticmethod
    def assign_permission_to_role(role_id, permission_id, actions=None):
        try:
            role = Role.query.get(role_id)
            permission = Permissions.query.get(permission_id)

            if not role or not permission:
                return {"error": "Role or Permission not found"}, 404

            # Store allowed actions for this role's permission
            if actions:
                permission.actions = ",".join(actions)

            role_permission = RolePermission(role=role, permission=permission)
            db.session.add(role_permission)
            db.session.commit()
            return {"success": f"Permission '{permission.name}' assigned to role '{role.name}'"}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error assigning permission to role: {e}")
            return {"error": "Internal server error"}, 500

    # ✅ Assign role to a user
    @staticmethod
    def assign_role_to_user(user_id, role_id, created_by=None):
        try:
            user = Users.query.get(user_id)
            role = Role.query.get(role_id)

            if not user or not role:
                return {"error": "User or Role not found"}, 404

            if any(ur.role_id == role.id for ur in user.user_roles):
                return {"error": "User already has this role"}, 400

            user_role = UserRole(user_id=user_id, role_id=role_id, created_by=created_by)
            db.session.add(user_role)
            db.session.commit()
            return {"success": f"Role '{role.name}' assigned to {user.email}"}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error assigning role to user: {e}")
            return {"error": "Internal server error"}, 500

    # ✅ Check if a user has a specific role
    @staticmethod
    def user_has_role(user_id, role_name):
        user = Users.query.get(user_id)
        if not user:
            return False
        return any(role.name == role_name for role in user.roles)

    # ✅ Check if a user has permission to perform an action
    @staticmethod
    def user_has_permission(user_id, permission_name, action=None):
        user = Users.query.get(user_id)
        if not user:
            return False

        for role in user.roles:
            for role_perm in role.role_permissions:
                if role_perm.permission.name == permission_name:
                    if action is None or action in role_perm.permission.action_list:
                        return True
        return False

    # ✅ Get all roles
    @staticmethod
    def get_all_roles():
        roles = Role.query.all()
        return [{"id": role.id, "name": role.name, "description": role.description} for role in roles]

    # ✅ Get all permissions
    @staticmethod
    def get_all_permissions():
        permissions = Permissions.query.all()
        return [{"id": perm.id, "name": perm.name, "group": perm.group, "actions": perm.action_list} for perm in permissions]

    # ✅ Remove role from user
    @staticmethod
    def remove_role_from_user(user_id, role_id):
        try:
            user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
            if not user_role:
                return {"error": "Role not assigned to user"}, 400

            db.session.delete(user_role)
            db.session.commit()
            return {"success": "Role removed successfully"}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error removing role: {e}")
            return {"error": "Internal server error"}, 500
