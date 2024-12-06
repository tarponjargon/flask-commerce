""" API routes related to the customer (User) """

import re
import hashlib
from urllib.parse import unquote
from flask import Blueprint, request, session, render_template, current_app
from flask_app.modules.email import send_email
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import decode_id, is_number, validate_email, sanitize, get_random_string
from flask_app.modules.http import get_env_vars, get_request_values
from flask_app.modules.order import get_order_by_id
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.user import (
    User,
    encrypt_password,
    get_customer_id_by_email,
    get_billing_fields,
    get_shipping_fields,
    get_id_by_email,
    create_user,
    password_compare,
)
from flask_app.modules.user.wishlist import get_hwlid, get_wishlist, delete_wishlist_item, upsert_wishlist_item

mod = Blueprint("account_api", __name__, url_prefix="/api")


@mod.route("/account")
def do_account():
    """Returns all user data as JSON"""
    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    user = User.from_id(customer_id)
    return user.get_account_data()


@mod.route("/updateaccount", methods=["POST"])
def do_updateaccount():
    """Updates the user account, returns all user data as JSON"""
    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    values = get_request_values()
    user = User.from_id(customer_id)
    resp = user.update_account_info(values)
    if resp["error"]:
        return resp

    return user.get_account_data()


@mod.route("/updateaddress", methods=["POST"])
def do_updateaddress():
    """Updates user address, returns all user data as JSON"""

    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    user = User.from_id(customer_id)

    values = get_request_values()

    if not values.get("TEMP_id"):
        return {"success": False, "error": True, "errors": ["No address passed"]}

    address_id = decode_id(values.get("TEMP_id"))
    if not is_number(address_id):
        return {"success": False, "error": True, "errors": ["Problem updating address.  Please contact us"]}

    res = user.upsert_address(values, address_id)
    if res["error"]:
        return res

    record_customer_activity(request_type="updateaddress")

    return user.get_account_data()


@mod.route("/newaddress", methods=["POST"])
def do_newaddress():
    """Creates a new customer address, returns all customer data as JSON"""
    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    user = User.from_id(customer_id)
    values = get_request_values()

    res = user.upsert_address(values)
    if res["error"]:
        return res

    record_customer_activity(request_type="newaddress")

    return user.get_account_data()


@mod.route("/deleteaddress", methods=["POST"])
def do_deleteaddress():
    """Deletes a user address, returns all customer data as JSON"""

    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    user = User.from_id(customer_id)
    values = get_request_values()

    if not values.get("address"):
        return {"success": False, "error": True, "errors": ["No address passed"]}

    address_id = decode_id(values.get("address"))
    if not is_number(address_id):
        return {"success": False, "error": True, "errors": ["Problem deleting address.  Please contact us"]}

    res = user.delete_address(address_id)
    if res["error"]:
        return res

    record_customer_activity(request_type="deleteaddress")

    return user.get_account_data()


@mod.route("/wishlist")
def do_wishlist():
    """Gets a user wishlist as JSON"""
    values = get_request_values()
    if not values.get("hwlid") or not len(values.get("hwlid")) == 32:
        return {"success": False, "error": True, "errors": ["No wishlist passed"]}

    return {
        "success": True,
        "error": False,
        "message": "Item(s) removed from your wishlist",
        "wishlist": get_wishlist(values.get("hwlid")),
    }


@mod.route("/wishlistupdate")
def do_wishlistupdate():
    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    values = get_request_values()
    if not values.get("wl_skuid"):
        return {"success": False, "error": True, "errors": ["No item passed"]}

    hwlid = get_hwlid(customer_id)

    res = upsert_wishlist_item(values.get("wl_skuid"), hwlid, values.get("wl_quantity"))
    if res["error"]:
        return res

    record_customer_activity(request_type="updatewishlist")

    return {
        "success": True,
        "error": False,
        "message": "Wishlist updated",
        "wishlist": get_wishlist(hwlid),
    }


@mod.route("/wishlistremove")
def do_wishlistremove():
    """Removes an item from the wishlist, returns updated wishlist as JSON"""
    values = get_request_values()

    if not values.get("hwlid") or not len(values.get("hwlid")) == 32:
        return {"success": False, "error": True, "errors": ["No wishlist passed"]}

    if not values.get("wl_skuid"):
        return {"success": False, "error": True, "errors": ["No item passed"]}

    res = delete_wishlist_item(values.get("wl_skuid"), values.get("hwlid"))
    if res["error"]:
        return res

    record_customer_activity(request_type="deletewishlistitem")

    return {
        "success": True,
        "error": False,
        "message": "Item(s) removed from your wishlist",
        "wishlist": get_wishlist(values.get("hwlid")),
    }


@mod.route("/wishlist-share", methods=["POST"])
def do_wishlist_share():
    """Shares a user wishlist with given emails, returns success or fail object as JSON"""
    values = get_request_values()
    if not values.get("hwlid") or not len(values.get("hwlid")) == 32:
        return {"success": False, "error": True, "errors": ["No wishlist passed"]}

    hwlid = values.get("hwlid")

    has_wishlist = DB.fetch_one("SELECT COUNT(*) as has_wl FROM wishlist WHERE hwlid = %(hwlid)s", {"hwlid": hwlid})[
        "has_wl"
    ]
    if not has_wishlist:
        return {"success": False, "error": True, "errors": ["Wishlist not found"]}

    if not values.get("wl_share_emails"):
        return {"success": False, "error": True, "errors": ["Please enter e-mails"]}

    emails = [i for i in unquote(values.get("wl_share_emails", [])).split()]

    if not all([validate_email(i) for i in emails]):
        return {"success": False, "error": True, "errors": ["Please check the format of the e-mail(s)"]}

    if len(emails) > 6:
        return {"success": False, "error": True, "errors": ["Max 6 e-mail addresses"]}

    # get wishlist owner's infop
    owner = DB.fetch_one(
        """
          SELECT
            IF(customers.bill_fname IS NULL or customers.bill_fname = 'Shopper', 'Your friend', customers.bill_fname) as bill_fname,
            IF(customers.bill_lname IS NULL or customers.bill_lname = '', '', customers.bill_lname) as bill_lname,
            customers.bill_email AS bill_email
          FROM customers, wishlist
          WHERE wishlist.hwlid = %(hwlid)s
          AND wishlist.customer_id = customers.customer_id
          LIMIT 1
        """,
        {"hwlid": hwlid},
    )
    owner_name = sanitize(owner.get("bill_fname") + " " + owner.get("bill_lname"))
    owner_email = sanitize(owner.get("bill_email"))

    for email in emails:
        send_email(
            subject=f"{owner_name} would like to share a {current_app.config['STORE_NAME']} Wishlist with You!",
            sender=current_app.config["DEFAULT_MAIL_SENDER"],
            recipients=[email],
            reply_to=owner_email,
            text_body=render_template(
                "emails/share_wishlist_email.html.j2", owner_name=owner_name, owner_email=owner_email, hwlid=hwlid
            ),
        )

    return {"success": True, "error": False}


@mod.route("/login", methods=["POST"])
def do_login():
    """User login route, returns success or fail object as JSON"""
    bill_email = request.form.get("bill_email")
    password = request.form.get("bill_account_password")
    login_error = 'Your login and/or password is incorrect. <a class="text-dark" href="javascript:void(0)" onclick="showCreateAccount(event)">Click here</a> to sign up, or <a class="text-dark" href="javascript:void(0)" onclick="showForgotPassword(event)">click here</a> if you forgot your password.'

    if not bill_email or not password:
        return {"success": False, "error": True, "errors": ["Please fill out all fields"]}

    if not validate_email(bill_email):
        return {"success": False, "error": True, "errors": ["Please enter an E-mail in the format you@yourdomain.com"]}

    customer_id = get_id_by_email(bill_email)
    if not customer_id:
        return {"success": False, "error": True, "errors": [login_error]}

    if not password_compare(customer_id, password):
        return {"success": False, "error": True, "errors": [login_error]}

    session["customer_id"] = customer_id
    user = User.from_id(customer_id)
    for key, val in user.get_user().items():
        session[key] = val

    record_customer_activity(request_type="login", email=bill_email)

    return {"success": True, "error": False}


@mod.route("/forgotpassword", methods=["POST"])
def do_forgotpassword():
    """Handles forgotpassword request, sends email if valid"""
    values = get_request_values()
    bill_email = values.get("bill_email")
    account_message = "If you have an account with us, you will receive an email with password reset instructions. If it does not arrive, please check your spam folder."

    if not bill_email or not validate_email(bill_email):
        return {"success": False, "error": True, "errors": ["Please enter an E-mail in the format you@yourdomain.com"]}

    customer_id = get_customer_id_by_email(bill_email)
    if not customer_id:
        return {"success": False, "error": True, "errors": [account_message]}

    token = hashlib.md5(get_random_string().encode("utf8")).hexdigest()
    success = DB.insert_query(
        "INSERT INTO cust_id_keys SET hash = %(token)s, customer_id = %(customer_id)s",
        {"token": token, "customer_id": customer_id},
    )
    if not success:
        password_error = 'Problem sending the password recovery link.  Please <a href="/contact">contact us</a> and we can help you.'
        return {"success": False, "error": True, "errors": [password_error]}

    send_email(
        subject=f"Reset Your {current_app.config['STORE_NAME']} Password",
        sender=current_app.config["STORE_EMAIL"],
        recipients=[bill_email],
        reply_to=current_app.config["DEFAULT_MAIL_SENDER"],
        text_body=render_template("emails/forgotpassword.txt.j2", email=bill_email, token=token),
    )

    return {"success": True, "error": False, "errors": [account_message]}


@mod.route("/checkpassword", methods=["POST"])
def do_checkpassword():
    """Checks the user password matches, returns success or fail response as JSON"""
    values = get_request_values()
    bill_email = values.get("bill_email")
    password = values.get("bill_account_password")
    login_error = "Password is incorrect"

    if not bill_email or not password:
        return {"success": False, "error": True, "errors": ["Please enter and e-mail and a password"]}

    if not validate_email(bill_email):
        return {"success": False, "error": True, "errors": ["Please enter an E-mail in the format you@yourdomain.com"]}

    customer_id = get_id_by_email(bill_email)
    if not customer_id:
        return {"success": False, "error": True, "errors": [login_error]}

    if not password_compare(customer_id, password):
        return {"success": False, "error": True, "errors": [login_error]}

    return {"success": True, "error": False}


@mod.route("/updatepassword", methods=["POST"])
def do_updatepassword():
    """Updates the user's password, returns a success or fail response as JSON"""
    values = get_request_values()
    password = values.get("bill_account_password")
    password_comfirm = values.get("bill_account_password_confirm")
    env_vars = get_env_vars()

    customer_id = session.get("customer_id")
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    if not password or not password_comfirm:
        return {"success": False, "error": True, "errors": ["Please enter password and confirmation password"]}

    # the regex makes sure the string has both letter(s) and number(s) with a lookahead
    if not password or len(password) < 8 or not re.match("^(?=.*?[0-9])(?=.*?[A-Za-z]).+", password):
        return {
            "success": False,
            "error": True,
            "errors": ["Please enter a password 8-24 chars, containing letters and numbers"],
        }

    if password != password_comfirm:
        return {"success": False, "error": True, "errors": ["New password does not match confirmation password"]}

    (salt, hashed_password) = encrypt_password(password)
    success = DB.update_query(
        """
          UPDATE customers SET
          md5_password = %(hashed_password)s,
          salt = %(salt)s,
          ins_or_upd = 'UPDATE',
          `date` = %(dt)s
          WHERE customer_id = %(customer_id)s
          LIMIT 1
        """,
        {"hashed_password": hashed_password, "salt": salt, "dt": env_vars.get("date"), "customer_id": customer_id},
    )
    if not success:
        return {"success": False, "error": True, "errors": ["Problem updating password.  Please contact us."]}

    record_customer_activity(request_type="updatepassword")

    return {"success": True, "error": False}


@mod.route("/newaccount", methods=["POST"])
def do_new_account():
    """Creates a new user account, returns success or fail response as JSON"""
    bill_email = request.form.get("bill_email")
    password = request.form.get("bill_account_password")
    password_confirm = request.form.get("bill_account_password_confirm")
    order_id = request.form.get("receipt_id")

    if not bill_email or not password or not password_confirm:
        return {"success": False, "error": True, "errors": ["Please fill out all fields"]}

    if not validate_email(bill_email):
        return {"success": False, "error": True, "errors": ["Please enter an E-mail in the format you@yourdomain.com"]}

    # the regex makes sure the string has both letter(s) and number(s) with a lookahead
    if not password or len(password) < 8 or not re.match("^(?=.*?[0-9])(?=.*?[A-Za-z]).+", password):
        return {
            "success": False,
            "error": True,
            "errors": ["Please enter a password 8-24 chars, containing letters and numbers"],
        }

    if password != password_confirm:
        return {"success": False, "error": True, "errors": ["Confirmation password does not match password"]}

    if get_customer_id_by_email(bill_email):
        return {
            "success": False,
            "error": True,
            "errors": [
                'An account already exists with that email.  \
                 <a href="javascript:void(0)" onclick="showForgotPassword(event)">Click here</a> if you forgot your password.'
            ],
        }

    customer_id = create_user(bill_email, password)
    if not customer_id:
        return {"success": False, "error": True, "errors": ["Problem creating account.  Please contact us."]}

    session["customer_id"] = customer_id
    user = User.from_id(customer_id)

    # if an order id is passed in AND the email on the order matches the email passed into this function
    # then, add the billing info to the account and the shipping info as an address
    if order_id and is_number(order_id):
        resp = get_order_by_id(order_id)
        if resp["order"]:
            order = resp["order"]
            if order and bill_email.casefold() == order.get("bill_email").casefold():
                # update the order with the customer ID so the order gets included in their account view
                upd = DB.update_query(
                    "UPDATE orders SET customer_id = %(customer_id)s WHERE order_id = %(order_id)s",
                    {"customer_id": customer_id, "order_id": order_id},
                )

                billing = get_billing_fields()
                billing_values = {}
                for field in billing:
                    billing_values[field] = order.get(field)
                user.update_account_info(billing_values)

                address_values = {}
                shipping = get_shipping_fields()
                for field in shipping:
                    address_values["TEMP_" + field] = order.get(field)
                user.upsert_address(address_values)

    # add user info to session
    for key, val in user.get_user().items():
        session[key] = val

    return {"success": True, "error": False}


@mod.route("/bbs-auth", methods=["POST"])
def do_bbs_auth():

    if current_app.config.get("STORE_CODE") != 'basbleu2':
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

    """Club validation rout returns success or fail object as JSON"""
    bill_email = request.form.get("bill_email")
    bill_lname = request.form.get("bill_lname")
    bill_zip = request.form.get("bill_postal_code")

    if not bill_email:
        return {"success": False, "error": True, "errors": ["Please enter your e-mail"]}

    if not validate_email(bill_email):
        return {"success": False, "error": True, "errors": ["Please enter an E-mail in the format you@yourdomain.com"]}

    if not bill_lname:
        return {"success": False, "error": True, "errors": ["Please enter your Last Name"]}

    if not bill_zip or not re.match(r"^\d{5}$", bill_zip):
        return {"success": False, "error": True, "errors": ["Please enter your 5-digit zip code"]}

    q = """
          SELECT custno,expiration,member_status
          FROM bb_society
          WHERE (lastname LIKE %(bill_lname)s AND zip LIKE %(bill_zip_like)s)
          OR email LIKE %(bill_email)s
          ORDER BY expiration DESC
          LIMIT 1
        """
    res = DB.fetch_one(q, {"bill_lname": bill_lname, "bill_zip_like": bill_zip + '%', "bill_email": bill_email})
    record_customer_activity(request_type="bbs-login", email=bill_email)
    if res.get('member_status') == 'E':
      session['BBSEXPIRED'] = True
      return {
          "success": False,
          "error": True,
          "errors": [
              "Your Bas Bleu Society membership has expired.  You can <a href='/add?item=12BBSRENEW'.html><b>click here to renew your membership</b></a>."
          ],
      }

    if res.get('member_status') == 'A':
      session['BBSVALIDATED'] = "1"
      session['BBSMEMBER'] = res.get('custno')
      return {
          "success": True,
          "error": False
      }

    return {
        "success": False,
        "error": True,
        "errors": [
            "We cannot find your Bas Bleu Society membership.  Please <a href=/12BASBLEU.html>Click here</a> to sign up."
        ],
    }