""" Functions related to payment during checkout """

import re
from datetime import datetime, timedelta
from flask import session, g, current_app

from flask_app.modules.http import session_get, session_safe_get


def check_payment_data():
    """Data validation for credit card payment fields.  Uses data already in the session

    Returns:
      dict: A success or fail payload that can be sent to the UI as JSON
    """

    # if this is a paypal order make sure wpp_* data is entered
    if session_get("payment_method") == "expresscheckout":
        if not session_get("wpp_token") or not session_get("wpp_payerid"):
            return {
                "success": False,
                "error": True,
                "errors": ["Please enter a valid payment method or re-authorize PayPal"],
            }
            current_app.logger.error("expresscheckout chosen but no wpp_token and/or wpp_payerid in session")
        else:
            return {
                "success": True,
                "error": False,
            }

    # if this is a giftcertificate and there is no final total, just return true
    if session_get("payment_method") == "giftcert" and not g.cart.get_total():
        return {
            "success": True,
            "error": False,
        }

    # if there is a worldpay token on the order, check that it's not > 23 hours old
    # do this by creating a session variable with the value of the worldpay_registration_id in the key, and the value being the time created
    # this makes sure that there is always a time value associated with whatever the current worldpay_registration_id is
    if session_get("worldpay_registration_id"):
      token_key = "wp_token_time_" + session_safe_get("worldpay_registration_id")
      if not session.get(token_key) or not re.match(r'^\d{14}$', session.get(token_key)):
        session[token_key] = datetime.now().strftime("%Y%m%d%H%M%S")

      token_time = datetime.strptime(session[token_key], "%Y%m%d%H%M%S")
      if (datetime.now() - token_time) > timedelta(hours=23):
        current_app.logger.error(f"worldpay token is > 23 hours old: {session[token_key]}")
        session["worldpay_registration_id"] = None
        return {
            "success": False,
            "error": True,
            "errors": ["Your payment session has expired, please re-enter your credit card information."],
        }
      else:
        current_app.logger.debug(f"worldpay token is current {session[token_key]} {token_key}")

    # check if worldpay has been interacted with.
    # if not, it's possible we're in a "fallback" state where worldpay is unavailable and we need to collect cc data directly
    if not session_get("credit_code"):
        required_worldpay = ["worldpay_registration_id", "card_month", "card_year", "card_type"]
        if not all([session.get(i) for i in required_worldpay]):
            return {
                "success": False,
                "error": True,
                "errors": ["Please complete all credit card fields"],
            }
        else:
            return {
                "success": True,
                "error": False,
            }

    # validate required fields have values
    credit_fields = [
        "credit_name",
        "credit_code",
        "credit_type",
        "credit_month",
        "credit_year",
        "credit_security_code",
    ]
    if not all([session.get(i) for i in credit_fields]):
        return {
            "success": False,
            "error": True,
            "errors": ["Please complete all credit card fields"],
        }

    # some crude credit card validation (if the card value is not masked, meaning it's already been done)
    credit_code = re.sub("[^x0-9]", "", session.get("credit_code"))
    credit_security_code = re.sub("[^x0-9]", "", session.get("credit_security_code"))
    if not re.match(r"^[x]{11,12}[0-9]{4}$", credit_code) and not re.match(
        r"^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$",
        credit_code,
    ):
        return {
            "success": False,
            "error": True,
            "errors": ["Please check your credit card number"],
        }

    if not re.match(r"^[x]{3,4}$", credit_security_code) and not re.match(r"^[0-9]{3,4}$", credit_security_code):
        return {
            "success": False,
            "error": True,
            "errors": [
                "Please check your credit card security code (CVV) on the back of your card, it should be either 3 or 4 digits long."
            ],
        }

    # save the raw card info to another key, mask inputted card code for UI
    if not re.match(r"^[x]{11,12}[0-9]{4}$", credit_code):
        session["credit_code_saved"] = credit_code
        session["credit_code"] = credit_code[-4:].rjust(len(credit_code), "x")

    # save raw cvv to another key, mask inputted value
    if not re.match(r"^[x]{3,4}$", credit_security_code):
        session["credit_security_code_saved"] = credit_security_code
        session["credit_security_code"] = re.sub(r"\d", "x", credit_security_code)

    # validate exp date
    if not re.match(r"^[0-9]{4}$", session.get("credit_year")) or not re.match(
        r"^[0-9]{2}$", session.get("credit_month")
    ):
        return {
            "success": False,
            "error": True,
            "errors": ["Please check your expiration date"],
        }

    card_expiration = int(session.get("credit_year") + session.get("credit_month") + "31")
    curdate = int(datetime.now().strftime("%Y%m%d"))
    if card_expiration < curdate:
        return {
            "success": False,
            "error": True,
            "errors": ["Your credit card appears to be expired"],
        }

    return {
        "success": True,
        "error": False,
    }


def clear_payment_data():
    """Delete any previously-set payment data in the session"""

    reset_keys = [
        "worldpay_registration_id",
        "worldpay_payment_token",
        "worldpay_vantiv_txn_id",
        "wpp_txn_id",
        "wpp_token",
        "wpp_payerid",
        "wpp_correlationid",
        "wpp_addressstatus",
        "wpp_paymentstatus",
        "wpp_payerstatus",
        "wpp_pendingreason",
        "wpp_tax",
        "wpp_total",
        "wpp_subtotal",
        "wpp_shipping",
        "payment_method",
    ]
    for delete_key in reset_keys:
        session[delete_key] = None
