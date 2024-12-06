""" API routes related to receipt lookup
Routes should be protected for customer service only
"""

from flask import Blueprint, Response, request, current_app, render_template, jsonify
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import sanitize
from flask_app.modules.http import api_route_error
from flask_app.modules.order import get_order_by_id, get_order_ids_by_email


mod = Blueprint("receipt_lookup_api", __name__)


@mod.route("/api/receipt", methods=["POST"])
def do_receipt_search():
    if request.form.get("order_lookup_email"):
        resp = get_order_ids_by_email(sanitize(request.form.get("order_lookup_email")))
        if resp.get("error"):
            return resp, 400
        return resp
    elif request.form.get("order_lookup_id"):
        resp = get_order_by_id(sanitize(request.form.get("order_lookup_id")))
        if resp.get("error"):
            return resp, 400
        return {"success": True, "error": False, "orderId": resp["order"]["order_id"]}
    else:
        return api_route_error("Please enter an order id or email", 400)
