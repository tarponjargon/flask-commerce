from datetime import datetime
from flask import g, current_app
from copy import copy
from pprint import pprint
from flask_app.modules.helpers import is_number, split_to_list

def apply_free_gift(discount=None):
    """Apply any active coupon-based free gift promo

    Args:
      discount (dict): The discount object (loaded from 'discounts')

    NOTE: this mutates the cart item(s) directly using .set
    """

    now = datetime.now()

    # if found but expired
    start_time = discount.get("start_timestamp") if isinstance(discount.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
    end_time = discount.get("end_timestamp") if isinstance(discount.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

    if start_time > now:
      return None
    if end_time < now:
      return None

    # found but spend threshold (discount['order_min']) is not met
    if g.cart.get_subtotal() < discount.get("order_min", 0):
        return None

    # if the 'discount' value is a skuid, it's a prerequesite in the cart
    if discount.get("discount") and \
      isinstance(discount.get("discount"), str) and \
      not is_number(discount.get("discount")) and \
      len(discount.get("discount")) > 3:

      if not g.cart.get_items_by_base_skuid(discount.get("discount")):
        return None

    # free gift choices are in discounts.item_level_discount_value
    promo_skuids = discount["item_level_discount_value"].strip()
    if not promo_skuids:
        return None

    my_skuids = split_to_list(promo_skuids)
    promo_items = g.cart.get_items_by_skuid_list(my_skuids)

    if not len(promo_items):
        return None

    # in the list of items returned, get the first one with a qty of 1.
    item = next((p for p in promo_items if p.get("quantity") == 1), None)
    if not item:
        return None

    item_price = copy(item.get("origprice")) if item.get("origprice") else copy(item.get("price"))
    item.set("price", 0.00)
    item.set("ppd1_price", item_price)
    item.set("is_tweaked", True)