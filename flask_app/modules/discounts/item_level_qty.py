from datetime import datetime
from flask import g, session, current_app
from copy import copy
from pprint import pprint
from flask_app.modules.helpers import is_number, split_to_list
from flask_app.modules.preload import get_discounts, get_product_promo_values, get_categories_products


def apply_item_level_qty_threshold(discount=None):
    """Applies an item-level qty threshold discount, like buy 10 get 10% off
    also works for "free shipping on 2 or more books"

    Args:
      discount (dict): The discount object (loaded from 'discounts')

    NOTE: this mutates the cart item(s) directly using .set
    """

    if not discount:
        discount = {}

    now = datetime.now()

    # if found but expired
    start_time = discount.get("start_timestamp") if isinstance(discount.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
    end_time = discount.get("end_timestamp") if isinstance(discount.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

    if start_time > now:
      return None
    if end_time < now:
      return None

    # a list of the eligible items
    promo_items = []

    cached_product_promos = get_product_promo_values()
    cached_categories_products = get_categories_products()

    # loop cart and find eligible items
    for item in g.cart.get_items():

      # item_level_discount_type = '1' means all items are discounted
      if discount["item_level_discount_type"] == "1":
          promo_items.append(item)

      # item_level_discount_type = '2' means it's a discount with a CLEARANCE_SPECIAL value
      # This is a way to arbitrarily group item together for promotions (like all items with CLEARANCE_SPECIAL: 5)
      # there can be multiple CLEARANCE_SPECIAL values, semicolon-delimited
      if discount["item_level_discount_type"] == "2":
          if item.get("unoptioned_skuid") in cached_product_promos["index"]:
              data = cached_product_promos["data"]
              for val in split_to_list(discount["item_level_discount_value"]):
                  f = next((i for i in data if i["skuid"] == item.get("unoptioned_skuid") and i["value"] == val), None)
                  if f:
                      promo_items.append(item)
                      break

      # item_level_discount_type = '3' means it's a discount on a category or group of categories
      # check sku against the index of categories->products to validate
      # there can be multiple categories specified (semicolon-delimited)
      if discount["item_level_discount_type"] == "3":
          for category in split_to_list(discount["item_level_discount_value"]):
              skus = cached_categories_products.get(category, [])
              if item.get("unoptioned_skuid") in skus:
                  promo_items.append(item)
                  break

      # item_level_discount_type = '4' means it's a discount on a SKU(s) specified
      # in discounts.item_level_discount_value
      # there can be multiple skus specified (semicolon-delimited)
      if discount["item_level_discount_type"] == "4":
          skus = split_to_list(discount["item_level_discount_value"])
          if item.get("unoptioned_skuid") in skus:
              promo_items.append(item)

    if not len(promo_items):
      return None

    # make sure hte minimum threshold is met
    eligible_qty = sum(item.get('quantity') for item in promo_items)

    # check if it's a tier
    discounts = get_discounts()
    coupon = g.promo_code
    matched = [i for i in discounts["data"] if coupon == i["code"]]

    # if there's more than 1 found, it's a tiered discount
    if len(matched) > 1:
      # sort hi to low
      matched = sorted(matched, key=lambda k: k["order_min"], reverse=True)
      qty_valid = False
      for disc in matched:
          if is_number(disc.get("discount")) and eligible_qty >= int(disc.get("order_min")):
              discount = disc
              qty_valid = True
              break
      if not qty_valid:
          discount = matched[-1]

    # found but qty threshold (discount['order_min']) is not met
    if eligible_qty < discount.get("order_min", 1):
        return None

    for cur_item in promo_items:
      cur_item.set("is_tweaked", True)
      if discount["discount_type"] == "8":
        product_price = copy(cur_item.get("price"))
        new_price = product_price * (1 - float(discount["discount"]))
        cur_item.set("price", new_price)
        cur_item.set("ppd1_price", product_price)
      elif discount["discount_type"] == "6" and discount["discount"] == "+0":
        cur_item.set("shipping", "+0")

