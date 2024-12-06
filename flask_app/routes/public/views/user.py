""" User view routes """

import re
from flask import Blueprint, current_app, render_template, session, redirect, request
from flask_app.modules.extensions import DB
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.user import User

mod = Blueprint("user_view", __name__)


@mod.route("/logout")
def do_logout_view():
    """Log out the customer (user)"""
    session.clear()
    return render_template("logout.html.j2")


@mod.route("/account")
def do_account_view():
    """Shows user account view if logged in, the login view if not"""
    if session.get("customer_id"):
        return render_template("account.html.j2")
    return render_template("login.html.j2")


@mod.route("/wishlistupdate")
def do_wishlistupdate_view():
    """Just a redirect to support legacy UI endpoint"""
    return redirect(current_app.config["STORE_URL"] + "/api/wishlistupdate?" + request.query_string.decode("utf8"))


@mod.route("/wishlistremove")
def do_wishlistremove_view():
    """Just a redirect to support legacy UI endpoint"""
    return redirect(current_app.config["STORE_URL"] + "/api/wishlistremove?" + request.query_string.decode("utf8"))


@mod.route('/shared-wishlist/<regex("([A-Za-z0-9]{32})"):hwlid>')
def do_sharedwishlist_view(hwlid):
    """View of a customer's wishlist available with a special hashed ID (for friends/family)"""
    return render_template("shared_wishlist.html.j2", hwlid=hwlid)


@mod.route("/resetpassword")
def do_resetpassword_view():
    """Reset password form"""

    token = request.values.get("key")
    if not token or not re.match(r"^[A-Za-z0-9]{32}$", token):
        errors = [
            'The key passed from your e-mail is not formatted correctly. Please <a href="/contact">contact us</a> for assistance.'
        ]
        return render_template("resetpassword.html.j2", errors=errors)

    res = DB.fetch_one(
        "SELECT customer_id FROM cust_id_keys WHERE hash = %(token)s AND timestamp > DATE_SUB(NOW(),INTERVAL 1 DAY)",
        {"token": token},
    )
    if not res or not res.get("customer_id"):
        errors = [
            'The key passed on your e-mail is either incorrect or expired. \
            Please try your <a href="javascript:;" onclick="showForgotPassword(event)">password recovery</a>\
            again or <a href="/contact">contact us</a> for assistance.'
        ]
        return render_template("resetpassword.html.j2", errors=errors)

    DB.delete_query("DELETE FROM cust_id_keys WHERE timestamp < DATE_SUB(NOW(),INTERVAL 1 DAY)")

    # log in the user
    session["customer_id"] = res.get("customer_id")
    user = User.from_id(res.get("customer_id"))
    user_data = user.get_user()
    for key, val in user_data.items():
        session[key] = val

    record_customer_activity(request_type="forgotpassword", email=user_data.get("bill_email"))

    return render_template("resetpassword.html.j2", errors=[])
