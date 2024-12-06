""" Receipt route Blueprint

Flask Blueprint for looking up order receipts by order ID, for customer service.
This should be protected from the public with basic auth at the webserver level
"""


from flask import Blueprint, render_template, current_app
from flask_app.modules.order import get_order_by_id
from flask_app.modules.helpers import sanitize
from flask_app.modules.http import page_not_found

mod = Blueprint("receiptlookup_view", __name__)


@mod.route("/receipt/order/<string:orderid>")
def do_test_receipt(orderid):
    """route for previewing order receipt page (not email)"""
    resp = get_order_by_id(sanitize(orderid))
    if not resp or resp["error"] or "order" not in resp:
        current_app.logger.info(f"No order found in order receipt lookup for {orderid}")
        current_app.logger.info(resp)
        return page_not_found(None)
    return render_template("receipt.html.j2", order=resp["order"])


@mod.route("/receipt")
def do_receiptlookup_search_view():
    """Render receipt lookup search page"""

    return render_template("receipt_lookup.html.j2")


@mod.route("/receipt/<string:orderid>")
def do_receiptlookup_view(orderid):
    """Render receipt view"""

    resp = get_order_by_id(sanitize(orderid))
    if not resp or resp["error"] or "order" not in resp:
        current_app.logger.info(f"No order found in receipt lookup for {orderid}")
        current_app.logger.info(resp)
        return page_not_found(None)

    # print(resp["order"])
    return render_template("emails/receipt.html.j2", order=resp["order"])
