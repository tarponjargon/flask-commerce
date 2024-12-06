""" Funtions related to product badges """

from datetime import timedelta, date

from flask import current_app
from flask_app.modules.extensions import DB, cache


def get_badges(product=None):
    """Determines if a CSS "corner badge" should appear

    Examples:
      "Clearance"
      "Sold Out"
      "Personalized"

    There can be more than one.  But if an item is NLA - that's the only badge

    Args:
      product_data (dict): The product data as a dictionary

    Returns:
      list: Each element contains a string - the css class to apply
    """
    css_classes = []

    if product is None or not product.get("skuid"):
        return css_classes

    # if product is nla, badge it as such and be done
    if product.get("nla"):
        css_classes.append("badge-sold-out")
        return css_classes

    # a product is "new" if creation_date < 90 days ago
    if product.get("creation_date"):
        creation = product.get("creation_date")
        days_between = date.today() - creation
        if days_between <= timedelta(days=90):
            css_classes.append("badge-new")

    # check for "sale" or "clearance" badge
    if product.get("origprice") or product.get("ppd1_price"):
        if product.get("category") and "clearance" in product.get("category"):
            css_classes.append("badge-clearance")
        else:
            css_classes.append("badge-sale")

    # "personalized" badge
    if product.get("custom"):
        css_classes.append("badge-personalized")

    return css_classes
