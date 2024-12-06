""" Checkout Routes Blueprint

Routes related to store checkout views
"""

import traceback
from flask import (
    Blueprint,
    current_app,
    render_template,
    session,
    g,
    current_app,
    g,
    redirect,
)
from flask_app.modules.checkout.billing import check_billing_shipping
from flask_app.modules.checkout.order import create_order
from flask_app.modules.checkout.paypal import (
    start_expresscheckout,
    return_expresscheckout,
    complete_expresscheckout,
)
from flask_app.modules.checkout.order_id import get_order_id
from flask_app.modules.checkout.payment import check_payment_data, clear_payment_data
from flask_app.modules.checkout.confirmation import check_confirmation_data
from flask_app.modules.email import send_email
from flask_app.modules.helpers import validate_email
from flask_app.modules.http import (
    get_request_values,
    session_get,
    error_500,
    get_cart_id,
)
from flask_app.modules.subscription import update_subscription
from flask_app.modules.user import User, get_id_by_email, password_compare
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.order import get_order_by_id, delete_order_session_keys
from flask_app.modules.extensions import DB

mod = Blueprint("checkout_view", __name__)


@mod.route("/checkout", methods=["GET", "POST"])
def do_checkout():
    """This route shows the checkout login or the billing/shipping page depending on session state (see below).
    Also handles the form posts from a checkout-login form or a guest checkout.
    I.e. will log the customer in or pass them on as a guest.

    if LOGINPASS or CUSTOMER_ID is set they have already passed login, so they are shown billing/shipping page.

    RETURNTOLOGIN param will force view of the login page even if above logic is true"""

    values = get_request_values()
    loginpass = session_get("LOGINPASS")
    customer_id = session_get("customer_id")
    request_type = values.get("REQUEST")
    login_return = values.get("returntologin")

    # make sure there are cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    missing_variant_item = g.cart.has_missing_variants()
    if missing_variant_item:
        return render_template(
            "missing_variants.html.j2",
            product=missing_variant_item.get("product"),
            removeskuid=missing_variant_item.get("skuid"),
        )

    # if the email doesn't exist in the customers table, add them default optin to 'yes'
    email_exists = (
        1
        if values.get("bill_email") and get_id_by_email(values.get("bill_email"))
        else 0
    )
    if not email_exists:
        update_subscription(values.get("bill_email"), "yes")

    # show billing if they are logged in or have already passed this step
    if (loginpass or customer_id) and not login_return:
        addresses = []
        if customer_id:
            user = User.from_id(customer_id)
            addresses = user.get_addresses()
        return render_template("billing.html.j2", addresses=addresses)

    if login_return:
        session["LOGINPASS"] = False

    # if a guest-checkout, simply collect a valid email and move on to billing/shipping
    if request_type == "guest":
        bill_email = values.get("bill_email")
        if not bill_email or not validate_email(bill_email):
            return render_template(
                "login_checkout.html.j2", errors=["Please enter a valid e-mail"]
            )
        record_customer_activity(request_type="guestlogin", email=bill_email)
        session["LOGINPASS"] = True
        return render_template("billing.html.j2", addresses=[])

    # if a login-checkout, process login
    if request_type == "login":
        bill_email = values.get("bill_email")
        password = values.get("bill_account_password")
        login_error = 'Your login and/or password is incorrect. <a class="text-dark" href="javascript:void(0)" onclick="showCreateAccount(event)">Click here</a> to sign up, or <a class="text-dark" href="javascript:void(0)" onclick="showForgotPassword(event)">click here</a> if you forgot your password.'

        if not bill_email or not password:
            return render_template(
                "login_checkout.html.j2", errors=["Please fill out all fields"]
            )

        if not validate_email(bill_email):
            return render_template(
                "login_checkout.html.j2", errors=["Please enter a valid e-mail"]
            )

        customer_id = get_id_by_email(bill_email)
        if not customer_id or not password_compare(customer_id, password):
            return render_template("login_checkout.html.j2", errors=[login_error])

        # set User to session
        session["customer_id"] = customer_id
        user = User.from_id(customer_id)
        for key, val in user.get_user().items():
            session[key] = val

        record_customer_activity(request_type="checkoutlogin", email=bill_email)

        return render_template("billing.html.j2", addresses=user.get_addresses())

    return render_template("login_checkout.html.j2")


@mod.route("/payment", methods=["GET", "POST"])
def do_payment():
    """This route shows the payment page or the billing/shipping page if there are errors
    Also handles the form posts for /payment.
    """

    # make sure there are cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    missing_variant_item = g.cart.has_missing_variants()
    if missing_variant_item:
        return render_template(
            "missing_variants.html.j2",
            product=missing_variant_item.get("product"),
            removeskuid=missing_variant_item.get("skuid"),
        )

    customer_id = session_get("customer_id")

    # need to make sure we have prior checkout step data
    if not session_get("bill_email"):
        return render_template(
            "login_checkout.html.j2", errors=["Please enter your e-mail or log in"]
        )

    # validate bill/ship is entered
    bill_ship_validation = check_billing_shipping()
    if bill_ship_validation["error"]:
        addresses = []
        if customer_id:
            user = User.from_id(customer_id)
            addresses = user.get_addresses()
        return render_template(
            "billing.html.j2",
            addresses=addresses,
            errors=bill_ship_validation.get("errors"),
        )

    # generate order_id and set to session
    if not session.get("order_id"):
        session["order_id"] = get_order_id()

    return render_template("payment.html.j2")


@mod.route("/confirmation", methods=["GET", "POST"])
def do_confirmation():
    """Shows the order confirmation page.  Also accepts POST data from the /payment route."""

    # make sure there are cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    missing_variant_item = g.cart.has_missing_variants()
    if missing_variant_item:
        return render_template(
            "missing_variants.html.j2",
            product=missing_variant_item.get("product"),
            removeskuid=missing_variant_item.get("skuid"),
        )

    customer_id = session_get("customer_id")

    # need to make sure we have prior checkout step data
    if not session_get("bill_email"):
        return render_template(
            "login_checkout.html.j2", errors=["Please enter your e-mail or log in"]
        )

    # validate bill/ship is entered
    bill_ship_validation = check_billing_shipping()
    if bill_ship_validation["error"]:
        addresses = []
        if customer_id:
            user = User.from_id(customer_id)
            addresses = user.get_addresses()
        return render_template(
            "billing.html.j2",
            addresses=addresses,
            errors=bill_ship_validation.get("errors"),
        )

    # check payment data is entered
    payment_validation = check_payment_data()
    if payment_validation.get("error"):
        return render_template(
            "payment.html.j2", errors=payment_validation.get("errors")
        )

    # final order checks/data validations
    # 3/27/24 - added try/except block to catch and log any errors rendering the confirmation page
    # once this is resolved please go back to
    # return render_template("confirmation.html.j2", ...
    confirmation_validation = check_confirmation_data()
    if confirmation_validation.get("error"):
        rendered_confirmation = None
        try:
            rendered_confirmation = render_template(
                "confirmation.html.j2", errors=confirmation_validation.get("errors")
            )
        except Exception as e:
            current_app.logger.error(
                "Error rendering confirmation.html.j2 (WITH USER ERROR) {}".format(e)
            )
            current_app.logger.info(
                "CART JSON WHEN ERROR OCCURRED: %s", g.cart.to_json()
            )
            current_app.logger.info("SESSION WHEN ERROR OCCURRED: %s", session)
            return error_500(None)

        return rendered_confirmation

    if not session.get("order_id"):
        session["order_id"] = get_order_id()

    rendered_confirmation = None
    try:
        rendered_confirmation = render_template("confirmation.html.j2")
    except Exception as e:
        current_app.logger.error("Error rendering confirmation.html.j2 {}".format(e))
        current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
        current_app.logger.info("CART: " + str(get_cart_id()))
        current_app.logger.info("CART JSON WHEN ERROR OCCURRED: %s", g.cart.to_json())
        current_app.logger.info("SESSION WHEN ERROR OCCURRED: %s", session)
        return error_500(None)

    return rendered_confirmation


@mod.route("/complete", methods=["POST"])
def do_receipt():
    """Creates an order, shows the receipt"""

    # make sure there are cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    missing_variant_item = g.cart.has_missing_variants()
    if missing_variant_item:
        return render_template(
            "missing_variants.html.j2",
            product=missing_variant_item.get("product"),
            removeskuid=missing_variant_item.get("skuid"),
        )

    customer_id = session_get("customer_id")

    user = None
    if customer_id:
        user = User.from_id(customer_id)

    # need to make sure we have prior checkout step data
    if not session_get("bill_email"):
        return render_template(
            "login_checkout.html.j2", errors=["Please enter your e-mail or log in"]
        )

    # validate bill/ship is entered
    bill_ship_validation = check_billing_shipping()
    if bill_ship_validation["error"]:
        addresses = []
        if user:
            addresses = user.get_addresses()
        return render_template(
            "billing.html.j2",
            addresses=addresses,
            errors=bill_ship_validation.get("errors"),
        )

    # check payment data is entered
    payment_validation = check_payment_data()
    if payment_validation.get("error"):
        return render_template(
            "payment.html.j2", errors=payment_validation.get("errors")
        )

    # final order checks/data validations
    confirmation_validation = check_confirmation_data()
    if confirmation_validation.get("error"):
        return render_template(
            "confirmation.html.j2", errors=confirmation_validation.get("errors")
        )

    if not session.get("order_id"):
        session["order_id"] = get_order_id()

    # make absolutely sure the order id is not already in the orders table
    # I don't actually know how this could happen but it does
    # if the email on the order is the same as the session, just show the order
    resp = get_order_by_id(str(session.get("order_id")))
    if resp and resp.get("order"):
        order = resp.get("order")
        if order.get("bill_email") == session.get("bill_email"):
            current_app.logger.error(
                "Prevented dupe order: {} email: {}".format(
                    order.get("order_id"), session.get("bill_email")
                )
            )
            session["order_temp"] = order.get("order_id")
            session["order_id"] = None
            g.cart.remove_all_items()
            delete_order_session_keys()
            return render_template("receipt.html.j2", order=order)

    # if this is a paypal order, report the order to paypal to "close the loop"
    if session_get("payment_method") == "expresscheckout":
        express_result = complete_expresscheckout()
        if express_result.get("error"):
            return render_template(
                "payment.html.j2", errors=express_result.get("errors")
            )

    # create the order
    order_result = create_order()
    if order_result.get("error"):
        return render_template(
            "confirmation.html.j2", errors=order_result.get("errors")
        )

    # if there's a gift certificate on the order, close it
    if session.get("giftcertificate"):
        upd = DB.update_query(
            "UPDATE gc_status SET gc_status = 'C' WHERE gc_code = %(giftcertificate)s",
            {"giftcertificate": session.get("giftcertificate")},
        )
        if not upd:
            current_app.logger.error(
                "Could not close gift certificate " + session.get("giftcertificate")
            )

    # if there's an expireable coupon on the order (starts with config.EXPIREABLE_COUPON_PREFIX), expire it
    if session_get("coupon_code", "").startswith(
        current_app.config["EXPIREABLE_COUPON_PREFIX"]
    ):
        upd = DB.update_query(
            "UPDATE discounts SET end_timestamp = DATE_SUB(NOW(), INTERVAL 1 DAY) WHERE code = %(coupon_code)s",
            {"coupon_code": session.get("coupon_code")},
        )
        if not upd:
            current_app.logger.error(
                "Could not expire coupon " + session.get("coupon_code")
            )

    # delete all items from the cart
    g.cart.remove_all_items()

    # set order ID to another variable
    session["order_temp"] = session.get("order_id")

    delete_order_session_keys()

    # delete the giftwrap sku string list from session
    # commented out because it will show the giftwrap as dissasociated in the cart
    # giftwrap_item = order.get_giftwrap_item()
    # if giftwrap_item:
    #     session["wrapped_" + giftwrap_item.get("skuid").lower()] = None

    # send email receipt to customer
    order_number = current_app.config["ORDER_PREFIX"] + str(session["order_temp"])
    # load the just-placed order from the database and use that for the email receipt data
    resp = get_order_by_id(str(session["order_temp"]))
    if not resp or resp["error"] or "order" not in resp:
        current_app.logger.error(
            f"No order found in receipt email process for {order_number}"
        )
        current_app.logger.error(resp)
    else:
        # current_app.logger.debug(resp["order"])
        send_email(
            subject=f"Your {current_app.config['STORE_NAME']} Order Receipt: {order_number}",
            sender=current_app.config["STORE_EMAIL"],
            recipients=[resp["order"]["bill_email"]],
            reply_to=current_app.config["DEFAULT_MAIL_SENDER"],
            html_body=render_template("emails/receipt.html.j2", order=resp["order"]),
        )

    # if logged in, update account
    if user:
        user.update_account_info(resp["order"])

    return render_template("receipt.html.j2", order=resp["order"])


@mod.route("/start-expresscheckout")
def do_start_expresscheckout():
    """Starts paypal express checkout"""

    # make sure there are cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    # clear any previously set payment data
    clear_payment_data()

    express_result = start_expresscheckout()
    if express_result.get("error"):
        return render_template(
            "login_checkout.html.j2", errors=express_result.get("errors")
        )

    return redirect(express_result["paypal_url"])


@mod.route("/return-expresscheckout")
def do_return_expresscheckout():
    """Return from expresscheckout"""

    # make sure there are still cart items
    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    express_result = return_expresscheckout()
    if express_result.get("error"):
        return render_template(
            "login_checkout.html.j2", errors=express_result.get("errors")
        )

    customer_id = session_get("customer_id")

    # make sure there's an email on the order
    if not session_get("bill_email"):
        return render_template(
            "login_checkout.html.j2", errors=["Please enter your e-mail"]
        )

    # check payment data is entered
    payment_validation = check_payment_data()
    if payment_validation.get("error"):
        return render_template(
            "payment.html.j2", errors=payment_validation.get("errors")
        )

    # validate bill/ship is entered
    bill_ship_validation = check_billing_shipping()
    if bill_ship_validation["error"]:
        addresses = []
        if customer_id:
            user = User.from_id(customer_id)
            addresses = user.get_addresses()
        return render_template(
            "billing.html.j2",
            addresses=addresses,
            errors=bill_ship_validation.get("errors"),
        )

    # assign an order_id
    if not session.get("order_id"):
        session["order_id"] = get_order_id()

    return render_template("confirmation.html.j2")


@mod.route("/reset-payment")
def do_reset_payment():
    """Route clears any previously-set payment data (in session) and redirects to the payment page"""

    clear_payment_data()

    return redirect("/payment")
