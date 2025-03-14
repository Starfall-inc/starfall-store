from flask import Blueprint, request, jsonify, render_template, g

admin_static_routes_bp = Blueprint("admin_static", __name__)


@admin_static_routes_bp.route('/')
def admin_index():
    return render_template('admin/index.html')
