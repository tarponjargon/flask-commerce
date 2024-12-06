""" Modules related to PayPal ExpressCheckout which has this general flow:

1.  Shopper clicks "checkout with paypal button"
2.  start_expressscheckoyt() runs and returns a paypal url to redirect customer to
3.  customer logs into paypal, OK's the payment and is returned to our site
4.  return_expresscheckout() runs, updating paypal with final order info
5.  Customer completes order
6.  complete_expresscheckout() runs, "closing the loop" with paypal by telling them the order is finished
"""

import requests
from urllib.parse import parse_qs
from flask import current_app, g, session, request
from flask_app.modules.http import session_get, get_session_id, get_cart_id
from flask_app.modules.helpers import sanitize


def start_expresscheckout():
    """Start the expresscheckout process using server-to-server login.
    Upon login, register the order-in-progress with paypal

    Returns:
      dict: A dictionary containing keys indicating success<bool>, error<bool>and,
            errors<list[str]> and paypal_url<str>
    """
    express_params = {
        "METHOD": "SetExpressCheckout",
        "USER": current_app.config["WPP_USER"],
        "PWD": current_app.config["WPP_PWD"],
        "SIGNATURE": current_app.config["WPP_SIG"],
        "VERSION": current_app.config["WPP_VERSION"],
        "PAYMENTREQUEST_0_PAYMENTACTION": current_app.config["WPP_PAYMENTACTION"],
        "PAYMENTREQUEST_0_ITEMAMT": g.cart.get_discounted(),
        "PAYMENTREQUEST_0_TAXAMT": g.cart.get_tax(),
        "PAYMENTREQUEST_0_SHIPPINGAMT": round(g.cart.get_shipping() + g.cart.get_surcharge(), 2),
        "PAYMENTREQUEST_0_AMT": g.cart.get_total(),
        "PAYMENTREQUEST_0_CURRENCYCODE": "USD",
        "RETURNURL": current_app.config["STORE_URL"] + "/return-expresscheckout",
        "CANCELURL": current_app.config["STORE_URL"],
        "REQCONFIRMSHIPPING": "1",
        "REQBILLINGADDRESS": "0",
    }

    try:
        r = requests.post(current_app.config["WPP_NVP_URI"], data=express_params, timeout=30)
        r.raise_for_status()
    except requests.exceptions.Timeout as errt:
        current_app.logger.error(errt)
    except requests.exceptions.ConnectionError as errc:
        current_app.logger.error(errc)
    except requests.exceptions.HTTPError as errh:
        current_app.logger.error(errh)
    except requests.exceptions.RequestException as err:
        current_app.logger.error(err)

    current_app.logger.info("PAYPAL EXPRESSCHECKOUT STARTING")
    current_app.logger.info("SESSION: " + str(get_session_id()))
    current_app.logger.info("CART: " + str(get_cart_id()))

    if not r:
        current_app.logger.error("Problem starting express checkout")
        return {
            "success": False,
            "error": True,
            "errors": [
                "We had a problem sending you to PayPal.  Please check out using another method.  We apologize for the inconvenience."
            ],
            "paypal_url": "",
        }
    current_app.logger.info("URL: " + str(r.request.url))
    current_app.logger.info("REQUEST BODY: " + str(r.request.body))
    current_app.logger.info("RESPONSE TEXT: " + str(r.text))

    params = parse_qs(r.text)

    if not params or not params.get("ACK") or not len(params["ACK"]) or not params["ACK"][0] == "Success":
        try:
            logmsg = params["L_LONGMESSAGE0"][0]
        except Exception as e:
            logmsg = "no response from paypal"
        current_app.logger.error(logmsg)
        return {
            "success": False,
            "error": True,
            "errors": [
                "We had a problem sending you to PayPal.  Please check out using another method.  We apologize for the inconvenience."
            ],
            "paypal_url": "",
        }
    paypal_url = current_app.config["WPP_PAYPAL_URI"] + "?cmd=_express-checkout&token=" + params["TOKEN"][0]
    current_app.logger.info("Redirecting to: " + paypal_url)

    return {"success": True, "error": False, "errors": [], "paypal_url": paypal_url}


def return_expresscheckout():
    """Called upon the return to our site from paypal login.  Tells paypal about any order updates

    Returns:
      dict: A dictionary containing keys indicating success<bool>, error<bool> and,
            errors<list[str]>
    """

    wpp_token = sanitize(request.values.get("token"))
    express_params = {
        "METHOD": "GetExpressCheckoutDetails",
        "VERSION": current_app.config["WPP_VERSION"],
        "USER": current_app.config["WPP_USER"],
        "PWD": current_app.config["WPP_PWD"],
        "SIGNATURE": current_app.config["WPP_SIG"],
        "TOKEN": wpp_token,
    }
    try:
        r = requests.post(current_app.config["WPP_NVP_URI"], data=express_params, timeout=30)
        r.raise_for_status()
    except requests.exceptions.Timeout as errt:
        current_app.logger.error(errt)
    except requests.exceptions.ConnectionError as errc:
        current_app.logger.error(errc)
    except requests.exceptions.HTTPError as errh:
        current_app.logger.error(errh)
    except requests.exceptions.RequestException as err:
        current_app.logger.error(err)

    current_app.logger.info("PAYPAL EXPRESSCHECKOUT RETURNING")
    current_app.logger.info("SESSION: " + str(get_session_id()))
    current_app.logger.info("CART: " + str(get_cart_id()))

    if not r:
        current_app.logger.error("Problem returning from express checkout")
        return {
            "success": False,
            "error": True,
            "errors": [
                "We had a problem communicating with PayPal.  Please check out using another method.  We apologize for the inconvenience."
            ],
            "paypal_url": "",
        }

    current_app.logger.info("URL: " + str(r.request.url))
    current_app.logger.info("REQUEST BODY: " + str(r.request.body))
    current_app.logger.info("RESPONSE TEXT: " + str(r.text))

    params = parse_qs(r.text)

    if not params or not params.get("ACK") or not len(params["ACK"]) or not params["ACK"][0] == "Success":
        try:
            logmsg = params["L_LONGMESSAGE0"][0]
        except Exception as e:
            logmsg = "Problem returning from paypal"
        if 'Invalid token' not in str(logmsg): # don't log invalid token errors
          current_app.logger.error("PayPal returned error: {}, order id: {}, email: {}".format(logmsg, session_get("order_id"), session_get("bill_email")))
        error_msg = "We encountered a problem returning from PayPal.  Please check out using another method.  We apologize for the inconvenience."
        if 'Invalid token' in str(logmsg):
            error_msg = "Your PayPal session has expired.  Please click the PayPal button again to continue.  We apologize for the inconvenience."
        return {
            "success": False,
            "error": True,
            "errors": [error_msg],
        }

    # parse_qs values come in key+list, convert to key+value
    c = {k: v[0] if len(v) else "" for k, v in params.items()}

    try:
        ship_name = c.get("SHIPTONAME").split(" ", 1)
    except Exception as e:
        current_app.logger.error("Problem splitting paypal shiptoname")
        current_app.logger.error(e)
        ship_name = [c.get("FIRSTNAME", ""), c.get("LASTNAME", "")]

    customer = {
        "bill_country": "CANADA" if c.get("COUNTRY", "") == "CA" else "USA",
        "ship_country": "CANADA" if c.get("SHIPTOCOUNTRYCODE", "") == "CA" else "USA",
        "wpp_token": wpp_token,
        "wpp_payerid": c.get("PAYERID"),
        "wpp_payerstatus": "Y" if c.get("PAYERSTATUS") == "verified" else "N",
        "wpp_addressstatus": "Y" if c.get("ADDRESSSTATUS") == "Confirmed" else "N",
        "payment_method": "expresscheckout",
        "bill_fname": c.get("FIRSTNAME"),
        "bill_lname": c.get("LASTNAME"),
        "bill_street": c["STREET"] if c.get("STREET") else c.get("SHIPTOSTREET"),
        "bill_city": c["CITY"] if c.get("CITY") else c.get("SHIPTOCITY"),
        "bill_state": c["STATE"] if c.get("STATE") else c.get("SHIPTOSTATE"),
        "bill_postal_code": c["ZIP"] if c.get("ZIP") else c.get("SHIPTOZIP"),
        "bill_email": c.get("EMAIL"),
        "bill_phone": c["PHONENUM"] if c.get("PHONENUM") else "NA",
        "ship_fname": ship_name[0] if len(ship_name) else c.get("FIRSTNAME"),
        "ship_lname": ship_name[1] if len(ship_name) > 1 else c.get("LASTNAME"),
        "ship_street": c.get("SHIPTOSTREET"),
        "ship_city": c.get("SHIPTOCITY"),
        "ship_state": c.get("SHIPTOSTATE"),
        "ship_postal_code": c.get("SHIPTOZIP"),
    }

    current_app.logger.info("PAYPAL RETURNED CUSTOMER DATA")
    current_app.logger.info("SESSION: " + str(get_session_id()))
    current_app.logger.info("CART: " + str(get_cart_id()))
    current_app.logger.info("CUSTOMER DATA: ")
    current_app.logger.info(customer)

    # add customer data returned from paypal to the session
    for k, v in customer.items():
        session[k] = v

    return {
        "success": True,
        "error": False,
        "errors": [],
    }


def complete_expresscheckout():
    """Upon completion of the order by the customer, send order details to PayPal to close the loop

    Returns:
      dict: A dictionary containing keys indicating success<bool>, error<bool>and an errors<list[str]>
    """
    express_params = {
        "METHOD": "DoExpressCheckoutPayment",
        "VERSION": current_app.config["WPP_VERSION"],
        "USER": current_app.config["WPP_USER"],
        "PWD": current_app.config["WPP_PWD"],
        "SIGNATURE": current_app.config["WPP_SIG"],
        "TOKEN": session_get("wpp_token"),
        "PAYERID": session_get("wpp_payerid"),
        "PAYMENTREQUEST_0_PAYMENTACTION": current_app.config["WPP_PAYMENTACTION"],
        "PAYMENTREQUEST_0_ITEMAMT": g.cart.get_discounted(),
        "PAYMENTREQUEST_0_TAXAMT": g.cart.get_tax(),
        "PAYMENTREQUEST_0_SHIPPINGAMT": round(g.cart.get_shipping() + g.cart.get_surcharge(), 2),
        "PAYMENTREQUEST_0_AMT": g.cart.get_total(),
        "PAYMENTREQUEST_0_CURRENCYCODE": "USD",
    }
    try:
        r = requests.post(current_app.config["WPP_NVP_URI"], data=express_params, timeout=30)
        r.raise_for_status()
    except requests.exceptions.Timeout as errt:
        current_app.logger.error(errt)
    except requests.exceptions.ConnectionError as errc:
        current_app.logger.error(errc)
    except requests.exceptions.HTTPError as errh:
        current_app.logger.error(errh)
    except requests.exceptions.RequestException as err:
        current_app.logger.error(err)

    current_app.logger.info("PAYPAL EXPRESSCHECKOUT COMPLETING")
    current_app.logger.info("SESSION: " + str(get_session_id()))
    current_app.logger.info("CART: " + str(get_cart_id()))

    if not r:
        current_app.logger.error("Problem returning from express checkout")
        return {
            "success": False,
            "error": True,
            "errors": [
                "We had a problem communicating with PayPal.  Please check out using another method.  We apologize for the inconvenience."
            ],
            "paypal_url": "",
        }

    current_app.logger.info("URL: " + str(r.request.url))
    current_app.logger.info("REQUEST BODY: " + str(r.request.body))
    current_app.logger.info("RESPONSE TEXT: " + str(r.text))

    params = parse_qs(r.text)

    if not params or not params.get("ACK") or not len(params["ACK"]) or not params["ACK"][0] == "Success":
        try:
            logmsg = params["L_LONGMESSAGE0"][0]
        except Exception as e:
            logmsg = "Problem returning from paypal"
        current_app.logger.error(logmsg)
        error_msg = "We encountered a problem communicating with PayPal. please choose another payment method.  We apologize for the inconvenience."
        if 'Invalid token' in str(logmsg):
            error_msg = "Your PayPal session has expired.  Please click the PayPal button again to continue.  We apologize for the inconvenience."
        return {
            "success": False,
            "error": True,
            "errors": [error_msg],
        }

    # parse_qs values come in key+list, convert to key+value
    r = {k: v[0] if len(v) else "" for k, v in params.items()}

    # put values returned from paypal into session
    paypal_response = {
        "wpp_txn_id": r.get("PAYMENTINFO_0_TRANSACTIONID"),
        "wpp_token": r.get("TOKEN"),
        "wpp_correlationid": r.get("CORRELATIONID"),
        "wpp_paymentstatus": r.get("PAYMENTINFO_0_PAYMENTSTATUS"),
        "wpp_reasoncode": r.get("PAYMENTINFO_0_REASONCODE"),
        "wpp_pendingreason": r.get("PAYMENTINFO_0_PENDINGREASON"),
    }

    current_app.logger.info("PAYPAL DOEXPRESSCHECKOUTPAYMENT RESPONSE")
    current_app.logger.info("SESSION: " + str(get_session_id()))
    current_app.logger.info("CART: " + str(get_cart_id()))
    current_app.logger.info("PAYPAL RESPONSE:")
    current_app.logger.info(paypal_response)

    # add customer data returned from paypal to the session
    for k, v in paypal_response.items():
        session[k] = v

    return {"success": True, "error": False, "errors": []}
