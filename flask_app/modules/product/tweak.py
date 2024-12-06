""" processes product tweaks.  a "tweak" allows for dynamic modification of the product data

NOTE: any price modification that happens in this module affects the *base* price of an item
i.e. before any variant upcharges are applied.
"""

from copy import copy
from flask import g, current_app, session
from flask_app.modules.preload import get_product_specials


def tweak_product(product_data):
    """Process product tweaks.  Receives product data, called before the product object is instantiated

    Args:
      product_data (dict): The product data

    Returns:
      dict: The mutated product data dictionary
    """

    # check if there is a product special (time-specific sale price)
    new_price = check_product_specials(product_data)
    if new_price:
        product_data.update(new_price)

    # check if the item is a pre-order
    preorder = check_preorder(product_data)
    if preorder:
        product_data.update(preorder)

    # check that gift certificates are shipped free
    shipped_free = check_free_shipping(product_data)
    if shipped_free:
        product_data.update(shipped_free)

    # current_app.logger.debug(product_data)
    return product_data


def check_product_specials(product_data):
    """
    Check if this item is a product special (a time-sensitive sale price)
    Args:
      product_data (dict): The product data

    Returns:
      dict: A dictionary containing the product keys to update
    """

    specials = {"index": []}
    try:
        specials = get_product_specials()
        if product_data["skuid"] in specials["index"]:
            p = next((i for i in specials["data"] if i["skuid"] == product_data.get("skuid")), None)
            if p and p["special_price"] > 0 and p["special_price"] < product_data["price"]:
                #current_app.logger.debug("special price found for {} {}".format(product_data.get("skuid"), p["special_price"]))
                return {
                  "price": p["special_price"],
                  "ppd1_price": copy(product_data["price"]),
                  "is_product_special": True,
                }
    except AttributeError as err:
        current_app.logger.error("Could not load product specials from cached " + str(err))

    return {}


def check_preorder(product_data):
    """
    Check if this item is a pre-order
    Args:
      product_data (dict): The product data

    Returns:
      dict: A dictionary containing the product keys to update
    """
    if product_data.get("preorder"):
        return {"name": "PRE-ORDER: " + product_data.get("name")}
    return {}

def check_free_shipping(product_data):
    """
    CHeck if this item is supposed to have free shipping.  This *should* be handled
    in the product record, but often is overlooked.  Particularly, this happens with the gift certificates

    Args:
      product_data (dict): The product data

    Returns:
      dict: A dictionary containing the product keys to update
    """
    if product_data.get("skuid") == 'GC9999' or product_data.get("skuid") == 'EC9999':
        return {"shipping": "+0"}
    return {}
