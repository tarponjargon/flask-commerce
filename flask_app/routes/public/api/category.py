""" Category API routes """

from flask import Blueprint, request
from flask_app.modules.category import Category
from flask_app.modules.helpers import serialize
from flask_app.modules.http import api_route_error

mod = Blueprint("category_api", __name__, url_prefix="/api")


@mod.route("/category/<path:path>")
def do_category(path):
    """Return category object as JSON"""
    category_code = request.path.split("/")[-1]
    category = Category.from_code(category_code, True)
    if category and category.get_category():
        return serialize(category.get_category())
    else:
        return api_route_error("Category not found")
