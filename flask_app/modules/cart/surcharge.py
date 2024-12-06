""" Functions related to surcharge calculations """

from flask_app.modules.http import session_get


def calculate_surcharge(subtotal):
    """Calculates surcharge

    Args:
      subtotal (float): Order subtotal before tax and shipping
    Returns:
      float: the surcharge
    """

    surcharge = 0.00

    # If the shipping state is CO, add 0.28
    if session_get("ship_state") == "CO":
        surcharge = 0.29

    # if the shipping state is MN and the order subtotal
    # is greater than or equal to 100, add .50 surcharge
    elif session_get("ship_state") == "MN" and subtotal >= 100:
        surcharge = 0.50

    return round(surcharge, 2)
