from flask import Blueprint, jsonify, request, session
from app.extensions import db
from app.models.admin_models import Users, Role, Permissions, UserRole, RolePermission
from app.utils.rbac_utils import require_permission

admin_bp = Blueprint("admin", __name__)

# ✅ Assign a role to a user
@admin_bp.route("/assign-role", methods=["POST"])
@require_permission("manage_roles", "assign")
def assign_role():
    data = request.json
    user = Users.query.get(data["user_id"])
    role = Role.query.get(data["role_id"])

    if not user or not role:
        return jsonify({"error": "User or Role not found"}), 404

    if role in user.roles:
        return jsonify({"message": "User already has this role"}), 200

    user_role = UserRole(user_id=user.id, role_id=role.id, created_by=session["user_id"])
    db.session.add(user_role)
    db.session.commit()

    return jsonify({"success": f"Role {role.name} assigned to {user.email}"}), 201

# ✅ Remove a role from a user
@admin_bp.route("/remove-role", methods=["POST"])
@require_permission("manage_roles", "remove")
def remove_role():
    data = request.json
    user = Users.query.get(data["user_id"])
    role = Role.query.get(data["role_id"])

    if not user or not role:
        return jsonify({"error": "User or Role not found"}), 404

    user.remove_role(role)
    db.session.commit()

    return jsonify({"success": f"Role {role.name} removed from {user.email}"}), 200

# ✅ Create a new role
@admin_bp.route("/create-role", methods=["POST"])
@require_permission("manage_roles", "create")
def create_role():
    data = request.json
    new_role = Role(name=data["name"], description=data.get("description", ""))
    db.session.add(new_role)
    db.session.commit()

    return jsonify({"success": f"Role {new_role.name} created successfully"}), 201

# ✅ Assign permissions to a role
@admin_bp.route("/assign-permission", methods=["POST"])
@require_permission("manage_permissions", "assign")
def assign_permission():
    data = request.json
    role = Role.query.get(data["role_id"])
    permission = Permissions.query.get(data["permission_id"])

    if not role or not permission:
        return jsonify({"error": "Role or Permission not found"}), 404

    role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
    db.session.add(role_permission)
    db.session.commit()

    return jsonify({"success": f"Permission {permission.name} assigned to {role.name}"}), 201
