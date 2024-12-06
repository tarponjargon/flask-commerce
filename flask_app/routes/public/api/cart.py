""" Cart API routes """
from flask import Blueprint, g

from flask_app.modules.helpers import serialize

mod = Blueprint("cart_api", __name__, url_prefix="/api")


@mod.route("/cart", methods=["GET", "POST"])
@mod.route("/add", methods=["GET", "POST"])
def do_cart_add():
    """For adding items to the cart via the API"""
    return {"cart": serialize(g.cart.to_dict(True))}


@mod.route("/cart/totals")
def do_ajax_carttotals():
    """Returns cart totals as JSON"""
    return {"quantities": g.cart.get_quantities(), "subtotal": g.cart.get_discounted()}
