""" Functions related to a customer's orders """

from flask_app.modules.extensions import DB


def get_tracking_link(tracking_number, ship_method_code):
    """Gets the tracking url for a shipment

    Args:
      tracking_number (str): The tracking number on the shipment
      ship_method_code (str): The shipping method code

    Returns:
      str: The tracking url
    """

    fedex_app_methods = ["10", "11", "12", "13", "14", "19", "29", "34", "53", "80", "81"]
    fedex_methods = ["30", "33", "35"]
    osm_methods = ["41", "42", "43"]
    usps_methods = ["05"]
    ups_methods = ["01", "02", "03", "06", "52"]
    dhl_methods = ["09", "32", "15"]

    if not tracking_number or not ship_method_code:
        return None

    tracking_number = str(tracking_number)
    ship_method_code = str(ship_method_code)

    if ship_method_code in fedex_app_methods:
        return f"fedex.com/fedextrack/?trknbr={tracking_number}"

    if ship_method_code in fedex_methods:
        return f"fedex.com/fedextrack/?trknbr={tracking_number}"

    if ship_method_code in osm_methods:
        return f"https://www.osmworldwide.com/tracking/?trackingNumbers={tracking_number}"

    if ship_method_code in usps_methods:
        return f"https://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?strOrigTrackNum={tracking_number}"

    if ship_method_code in ups_methods:
        return f"https://wwwapps.ups.com/WebTracking/track?track=yes&trackNums={tracking_number}"

    if ship_method_code in dhl_methods:
        return (
            f"https://www.dhl.com/us-en/home/tracking/tracking-ecommerce.html?submit=1&tracking-id={tracking_number}"
        )
