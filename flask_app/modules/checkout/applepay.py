""" Function related to checkout with applepay """

import requests
import socket
import os
from flask import current_app, g, request, session, current_app
from flask_app.modules.http import session_get


def get_applepay_tax():
    """Accepts shipping location data from applepay which allows us to calculate tax.  Default to

    Returns:
      dict: A dictionary of order data specifically for applepay consumption
    """
    values = request.values if request.values else {}
    current_app.logger.debug("APPLEPAY GET TAX REQUEST")
    current_app.logger.debug(values)
    country = values.get("countryCode", session_get("ship_country"))
    session["ship_country"] = "USA" if country == "US" else country
    country = values.get("countryCode", session_get("ship_country"))
    session["ship_state"] = values.get("administrativeArea", session_get("ship_state"))
    session["ship_city"] = values.get("locality", session_get("ship_city"))
    session["ship_postal_code"] = values.get("postalCode", session_get("ship_postal_code"))

    data = {
        "newTotal": {"label": "Order Total", "type": "final", "amount": g.cart.get_total()},
        "newLineItems": [
            {"type": "final", "label": "Subtotal", "amount": g.cart.get_discounted()},
            {"type": "final", "label": "Shipping", "amount": g.cart.get_shipping()},
            {"type": "final", "label": "Tax", "amount": g.cart.get_tax()},
        ],
    }
    current_app.logger.debug("APPLEPAY GET TAX RESPONSE")
    current_app.logger.debug(data)
    return data


def post_to_apple(url, keyfile, certfile, postdata):
    reqs = None
    requests_error = ""
    resultdata = []
    certfiles = (certfile, keyfile)
    current_app.logger.debug("APPLEPAY POST DATA")
    current_app.logger.debug(postdata)
    try:
        reqs = requests.post(url, cert=certfiles, json=postdata, verify=False)
    except requests.exceptions.RequestException as err:
        requests_error = "POST exception error to " + url + ": " + str(err)
    except socket.timeout as err:
        requests_error = str(err)
    try:
        reqs.raise_for_status()
    except requests.exceptions.HTTPError as err:
        requests_error = "POST HTTP error " + str(err)
        current_app.logger.error("ApplePay POST HTTP error " + str(err))
    except AttributeError as err:
        requests_error = "POST HTTP failure " + str(err)
        current_app.logger.error("ApplePay POST HTTP failure " + str(err))
    if reqs:
        if reqs.status_code == 200 or reqs.status_code == 201 or reqs.status_code == 202:
            resultdata = reqs.json()
            if len(resultdata) > 0:
                requests_error = ""
            else:
                requests_error = "POST success but blank response"
                current_app.logger.error("ApplePay POST success but blank response")
        else:
            requests_error = "POST connect but error status: [" + str(reqs.status_code) + "] " + reqs.text
            current_app.logger.error(
                "ApplePay POST connect but error status: [" + str(reqs.status_code) + "] " + reqs.text
            )
    else:
        if requests_error == "":
            requests_error = "POST undetermined connect error to " + url
            current_app.logger.error("ApplePay POST undetermined connect error to " + url)

    return (requests_error, resultdata)


def do_applepay_merchant_validation():
    mid_url = current_app.config["APPLEPAY_MERCHID_ENDPOINT"]
    mid = current_app.config["APPLEPAY_MERCHID"]
    mid_key_file = current_app.config["APPLEPAY_MERCHID_KEY"]
    mid_cert_file = current_app.config["APPLEPAY_MERCHID_CERT"]
    mid_display = current_app.config["STORE_NAME"]
    mid_initcxt = current_app.config["APPLEPAY_MERCHID_INIT_CONTEXT"]

    # Make sure the key and cert files are accessible in CGI-BIN
    mid_key_file_path = current_app.config["APP_ROOT"] + "/" + mid_key_file
    if not os.path.isfile(mid_key_file_path):
        current_app.logger.error("MID key not found " + mid_key_file_path)
        return {"error": "MID key not found"}

    mid_cert_file_path = current_app.config["APP_ROOT"] + "/" + mid_cert_file
    if not os.path.isfile(mid_cert_file_path):
        current_app.logger.error("MID cert not found: " + mid_cert_file_path)
        return {"error": "MID certy not found"}

    postdata = {
        "merchantIdentifier": mid,
        "displayName": mid_display,
        "initiative": "web",
        "initiativeContext": mid_initcxt,
    }
    current_app.logger.debug(f"ApplePay auth {mid_url}, {mid_key_file_path}, {mid_cert_file_path}")
    current_app.logger.debug(postdata)
    response = post_to_apple(mid_url, mid_key_file_path, mid_cert_file_path, postdata)
    current_app.logger.debug("APPLEPAY MERCHANT LOGIN RESPONSE")
    current_app.logger.debug(response)
    if len(response[0]) > 0:
        return {"error": response[0]}
    else:
        return response[1]


def do_applepay_complete_payment():
    current_app.logger.debug("Process applepay payment completion")
    jsonout = None
    order_total = g.cart.get_total()
    outdata = {"newTotal": {"label": "Order Total", "type": "final", "amount": order_total}}
    if float(order_total) > 0.0:
        jsonout = outdata
    else:
        jsonout = {"error": "Invalid Order Total"}
    current_app.logger.debug(jsonout)

    return jsonout


def add_applepay_customer():
    """Adds applepay customer to session"""
    if not request.values:
        return {"error": True, "success": False, "message": "No data received"}
    values = request.values
    current_app.logger.debug("APPLEPAY ADD CUSTOMER")
    current_app.logger.debug(values)

    session["payment_method"] = "applepay"
    session["bill_fname"] = values.get("billingContact[givenName]", "")
    session["bill_lname"] = values.get("billingContact[familyName]", "")
    session["bill_street"] = values.get("billingContact[addressLines][0]", "")
    session["bill_street2"] = values.get("billingContact[addressLines][1]", "")
    session["bill_city"] = values.get("billingContact[locality]", "")
    session["bill_state"] = values.get("billingContact[administrativeArea]", "")
    session["bill_postal_code"] = values.get("billingContact[postalCode]", "")
    session["bill_phone"] = values.get("shippingContact[phoneNumber]", "")
    session["bill_email"] = values.get("shippingContact[emailAddress]", "")
    session["ship_fname"] = values.get("shippingContact[givenName]", "")
    session["ship_lname"] = values.get("shippingContact[familyName]", "")
    session["ship_street"] = values.get("shippingContact[addressLines][0]", "")
    session["ship_street2"] = values.get("shippingContact[addressLines][1]", "")
    session["ship_city"] = values.get("shippingContact[locality]", "")
    session["ship_state"] = values.get("shippingContact[administrativeArea]", "")
    session["ship_postal_code"] = values.get("shippingContact[postalCode]", "")

    bill_country = values.get("billingContact[countryCode]", "")
    ship_country = values.get("shippingContact[countryCode]", "")
    session["bill_country"] = "USA" if bill_country == "US" else bill_country
    session["ship_country"] = "USA" if ship_country == "US" else ship_country

    return {"error": False, "success": True, "message": "Updated"}
