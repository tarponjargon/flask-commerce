""" Functions related to confirmation view """
import re
from flask import g, session, current_app


def check_confirmation_data():
    """Data validation for the confirmation page

    Returns:
      dict: A success or fail payload, can be sent to the client as JSON
    """

    # if they chose canada as a ship country make sure this brand ships there, and make sure they chose "canada" as ship method
    if session.get("ship_country") == "CANADA" and "CANADA" in current_app.config['SHIPPING_COUNTRIES'] \
      and session.get("ship_method") and session.get("ship_method") != '82':
      return {
          "success": False,
          "error": True,
          "errors": [f"Please change your shipping method to 'Canada'"],
      }

    # if they chose USA as a ship country make sure they didn't choose "canada" as ship method
    if session.get("ship_country") == "USA" \
      and session.get("ship_method") and session.get("ship_method") == '82':
      return {
          "success": False,
          "error": True,
          "errors": [f"Please select a US shipping method"],
      }

    # make sure they live in the lower 48 if choosing an expedited shipping method
    if session.get("ship_state") not in ['AL','AZ','AR','CA','CO','CT','DE','DC','FL','GA','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'] \
      and session.get("ship_method") and session.get("ship_method") in ['52','06','01']:
        return {
            "success": False,
            "error": True,
            "errors": [f"We're very sorry, but we can only expedite your order if you live within the Continental U.S. Please select 'Standard' as your shipping method."],
        }

    # do not allow any method other than standard and rush to go to PO boxes
    if session.get("ship_street") and session.get("ship_method") and session.get("ship_method") not in ['06','24']:
      addr = session.get("ship_street", "") + session.get("ship_street2", "")
      addr = addr.lower()
      addr = re.sub(r'[^a-zA-Z0-9]', '', addr)
      if 'pobox' in addr:
        return {
            "success": False,
            "error": True,
            "errors": [f"Your chosen shipping method is not available for PO Boxes. Please provide a street address or select \"Standard\" or \"Rush\" as your shipping method."],
        }

    # check if they are trying to ship drop-ship items to PO boxes
    if g.cart.has_drop_ship() and session.get("ship_street"):
      addr = session.get("ship_street", "") + session.get("ship_street2", "")
      addr = addr.lower()
      addr = re.sub(r'[^a-zA-Z0-9]', '', addr)
      if 'pobox' in addr:
        return {
            "success": False,
            "error": True,
            "errors": [f"Drop-ship items are unable to be shipped to PO Boxes. Please provide a street address for your shiping address"],
        }


    # check if any items on the order are restricted to continental US only and if so, that they don't have a shipping address
    # outside the continental US
    if session.get("ship_country") == "CANADA" and "CANADA" in current_app.config['SHIPPING_COUNTRIES'] \
      or session.get("ship_state") in ['AK', 'HI', 'PR', 'AA', 'AE', 'APO', 'FPO', 'PW', 'VI', 'GU']:

      lower_48 = g.cart.has_lower_48_only()
      if len(lower_48):
        names = [i.get('name') for i in lower_48]
        lower_48_str = ", ".join(names)
        return {
            "success": False,
            "error": True,
            "errors": [f"The following items cannot be shipped outside the Continental US: {lower_48_str}"],
        }

    # check if any items on the order are restricted to US only
    if session.get("ship_country") == "CANADA" and "CANADA" in current_app.config['SHIPPING_COUNTRIES']:
      us_only = g.cart.has_us_only()
      if len(us_only):
        names = [i.get('name') for i in us_only]
        us_only = ", ".join(names)
        return {
            "success": False,
            "error": True,
            "errors": [f"The following items cannot be shipped outside the US: {us_only}"],
        }

    return {
        "success": True,
        "error": False,
    }
