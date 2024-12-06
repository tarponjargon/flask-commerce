""" Checkout API routes """
import re
from flask import Blueprint, session, g
from flask_app.modules.checkout.billing import check_billing_shipping
from flask_app.modules.checkout.payment import check_payment_data
from flask_app.modules.checkout.order_id import get_order_id
from flask_app.modules.checkout.applepay import (
    do_applepay_merchant_validation,
    do_applepay_complete_payment,
    get_applepay_tax,
    add_applepay_customer,
)
from flask_app.modules.helpers import format_currency
from flask_app.modules.http import session_get, get_request_values

mod = Blueprint("checkout_api", __name__, url_prefix="/api")


@mod.route("/checkout/get_order_id")
def do_get_order_id():
    """Gets an orderID that's already set.  if there's not one, it  sets one to the session and returns it
    Don't return an order ID if there's no order total
    """

    order_id = session_get("order_id")
    message = ""
    if g.cart.is_empty():
        return {"orderid": "", "error": True, "message": "No items in cart"}
    if not order_id:
        order_id = get_order_id()
        session["order_id"] = order_id
        message = "New order ID"
    return {"orderid": str(order_id), "error": False, "message": message if message else "Existing order ID"}


@mod.route("/checkout/billingshipping", methods=["POST"])
def do_ajax_billingshipping():
    """Handles form submits from the billing/shipping page.  Since POST values
    are automatically added to the session, just check that the required values exist
    (in the *session*, not the request)
    """

    return check_billing_shipping()


@mod.route("/checkout/payment", methods=["POST"])
def do_ajax_payment():
    """Handles credit card data submitted from the payment page, this
    route is only called if the secure payment iframe doesn't load"""

    return check_payment_data()


@mod.route("/checkout/gc", methods=["POST"])
def do_ajax_gc():
    """Handles gift certificate messaging.  The actual redemption happens in the cart"""
    credit_total = g.cart.get_credit()
    total_order = g.cart.get_total()
    values = get_request_values()
    gc = re.sub(r"\W+", "", session_get("giftcertificate")) if values.get("giftcertificate") else None
    gc_amt = re.sub("[^0-9^.]", "", session_get("gc_amt")) if values.get("gc_amt") else None

    if not gc or not re.match(r"^[0-9a-zA-Z]{8,}", gc):
        session["giftcertificate"] = None
        return {"success": False, "error": "Please check certificate code"}

    if not gc_amt or not re.match(r"^\d*[.]?\d*$", gc_amt):
        session["giftcertificate"] = None
        return {"success": False, "error": "Please enter the amount of the gift certificate"}

    if credit_total:
        # if there is no order total, the gc credit covers entire order
        session["payment_method"] = "giftcert"
        if not total_order:
            return {
                "success": True,
                "additional_payment": False,
                "message": "The certificate covers the entire amount of your order, \
                  so additional payment is not necessary.  You will receive a refund \
                  for any balance. Please continue with your order.",
            }
        else:
            return {
                "success": True,
                "additional_payment": True,
                "message": format_currency(credit_total)
                + " has been deducted from your order total, leaving a balance of "
                + format_currency(total_order)
                + ".  Please enter payment information.",
            }
    else:
        session["giftcertificate"] = None
        return {"success": False, "error": "Gift certificate is not valid.  Please re-check."}


@mod.route("/checkout/start-applepay")
def do_start_applepay():
    """Starts applepay by validating merchant session"""

    return do_applepay_merchant_validation()


@mod.route("/checkout/get_applepay_tax", methods=["POST"])
def do_get_applepay_tax():
    """Gets tax for an applepay order"""

    return get_applepay_tax()


@mod.route("/checkout/complete-applepay")
def do_complete_applepay():
    """Completes applepay transaction"""

    return do_applepay_complete_payment()


@mod.route("/checkout/applepay_payment_authorized", methods=["POST"])
def do_payment_authorized():
    """adds applepay customer data"""

    return add_applepay_customer()
