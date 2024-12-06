from flask import g, current_app
from copy import copy
from pprint import pprint
import math
from flask_app.modules.helpers import split_to_list, format_currency, is_number
from flask_app.modules.preload import get_product_promo_values
from flask_app.modules.preload import (
  get_discounts,
  get_product_promo_values,
  get_categories_products
)

def group_min_spend_discount(discount=None):
    """Apply discounton min spend from item group

    Args:
      discount (dict): The discount object (loaded from 'discounts')

    Returns:
      None: Items are mutated directly

    """

    if not discount:
        discount = {}


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

    # make sure then minimum threshold is met
    eligible_subtotal = sum([float(item.get("product", {}).get("pristine_price")) * item.get('quantity') for item in promo_items])

    # found but qty threshold (discount['order_min']) is not met
    if eligible_subtotal < float(discount.get("order_min", 1)):
        return None

    num = discount["discount"]

    for item in promo_items:
      newprice = item.get("price")
      current_app.logger.debug("NEWPRICE {}".format(newprice))

      # if the discount is a number and value is >1 it's a $-off discount
      current_app.logger.debug("discount type: {}".format(discount["discount_type"]))
      if discount["discount_type"] == "11" and is_number(num) and float(num) > 1 and float(num) < item.get("price"):
          newprice = item.get("price") - float(num)

      # the discount is a percentage (0.10), apply %-off discount
      elif discount["discount_type"] == "11" and is_number(num) and float(num) < 1 and float(num) > 0:
          newprice = item.get("price") * (1 - float(num))

      # if the discount price has been set, set ppd1_price to the original item price
      if newprice and newprice < item.get("price"):
          item.set("ppd1_price", copy(item.get("price")))
          item.set("is_tweaked", True)
          item.set("price", newprice)