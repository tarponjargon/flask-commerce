""" Functions related to billing and shipping entry """
import re
from flask import session, current_app
from flask_app.modules.http import session_get


def check_billing_shipping():
    """Data validation for the billing/shipping page

    Returns:
      dict: A success or fail payload, can be sent to the client as JSON
    """
    required_billing = ["bill_fname", "bill_lname", "bill_street", "bill_city", "bill_state", "bill_postal_code"]
    required_shipping = ["ship_fname", "ship_lname", "ship_street", "ship_city", "ship_state", "ship_postal_code"]

    # check required billing
    if not all([session_get(i, "").strip() for i in required_billing]):
        return {
            "success": False,
            "error": True,
            "errors": ["Required billing fields: name, address 1, city, state, postal code"],
        }

    # check required shipping
    if not all([session_get(i, "").strip() for i in required_shipping]):
        return {
            "success": False,
            "error": True,
            "errors": ["Required shipping fields: name, address 1, city, state, postal code"],
        }

    # check for instances of billing street1 field only having numbers
    if re.match(r"^[0-9]{1,}$", session_get("bill_street")):
        return {
            "success": False,
            "error": True,
            "errors": ["Your billing address (line 1) contains only numbers.  Please include a street name."],
        }

    # check for instances of shipping street1 field only having numbers
    if re.match(r"^[0-9]{1,}$", session_get("ship_street")):
        return {
            "success": False,
            "error": True,
            "errors": ["Your shipping address (line 1) contains only numbers.  Please include a street name."],
        }

    # check that billing city has at least 3 alnum characters
    if not re.match(r"[a-zA-Z0-9]{3,}", session_get("bill_city")):
        return {
            "success": False,
            "error": True,
            "errors": ["Please check your billing city"],
        }

    # check that shipping city has at least 3 alnum characters
    if not re.match(r"[a-zA-Z0-9]{3,}", session_get("ship_city")):
        return {
            "success": False,
            "error": True,
            "errors": ["Please check your shipping city"],
        }


    # BILLING if they are USA, make sure their postal code and zip4 are formatted correctly
    if session_get("bill_country") == "USA":
        # if zip is entered as zip and zip+4, split them out into separate fields
        res = re.search(r"^([0-9]{5})\-([0-9]{4})$", session_get("bill_postal_code"))
        if res and res.groups and len(res.groups()):
            session["bill_postal_code"] = res.group(1)
            session["bill_zip_4"] = res.group(2)

        if not re.match(r"^[0-9]{5}$", session_get("bill_postal_code")):
            return {
                "success": False,
                "error": True,
                "errors": ["Please check your billing zip code. It should be formatted 12345 or 12345-0001"],
            }

    # SHIPPING if they are USA, make sure their postal code and zip4 are formatted correctly
    if session_get("ship_country") == "USA":
        # if zip is entered as zip and zip+4, split them out into separate fields
        res = re.search(r"^([0-9]{5})\-([0-9]{4})$", session_get("ship_postal_code"))
        if res and res.groups and len(res.groups()):
            session["ship_postal_code"] = res.group(1)
            session["ship_zip_4"] = res.group(2)

        if not re.match(r"^[0-9]{5}$", session_get("ship_postal_code")):
            return {
                "success": False,
                "error": True,
                "errors": ["Please check your shipping zip code. It should be formatted 12345 or 12345-0001"],
            }

    # check valid ship country
    if session_get("ship_country") and session_get("ship_country") not in current_app.config['SHIPPING_COUNTRIES']:
      shipping_countries = ", ".join(current_app.config['SHIPPING_COUNTRIES'])
      return {
          "success": False,
          "error": True,
          "errors": [f"Unfortunately we do not ship outside of {shipping_countries} at this time."],
      }

    # do not allow orders to be placed that ship to remote canadian provinces
    if re.match(
        r"^A0K|^A0P|^A0R|^A2V|^G0G|^G4T|^J0M|^R0B|^T0P|^T0V|^V0L|^V0T|^V0V|^V0W|^X0A|^Y9Z",
        session_get("ship_postal_code"),
    ):
        return {
            "success": False,
            "error": True,
            "errors": [
                "Regrettably we cannot ship orders to your location at this time.  Please <a href='/contact'>contact us</a> with any questions."
            ],
        }

    return {
        "success": True,
        "error": False,
    }
