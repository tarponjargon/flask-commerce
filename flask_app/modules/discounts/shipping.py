from flask import g, current_app
from copy import copy
from pprint import pprint
import math
from flask_app.modules.helpers import split_to_list, format_currency
from flask_app.modules.preload import get_product_promo_values
from flask_app.modules.preload import (
  get_discounts,
  get_product_promo_values,
  get_categories_products
)

def group_min_spend_shipping_discount(discount=None):
    """Apply Free/flat shipping on min spend from item group

    Args:
      discount (dict): The discount object (loaded from 'discounts')

    Returns:
      tuple: (str, float) The discount amount as a string and the remaining amount to reach the threshold if any

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

    # for item in promo_items:
    #     current_app.logger.debug("Promo item: %s" % item.get("unoptioned_skuid"))

    # make sure then minimum threshold is met
    eligible_subtotal = round(sum([float(item.get_total_price()) for item in promo_items]), 2)

    # found but qty threshold (discount['order_min']) is not met
    if eligible_subtotal < float(discount.get("order_min", 1)):
        return ("", float(discount.get("order_min", 1) - eligible_subtotal))

    # if there are non-eligible items on the order, make the offer flat shipping 9.99
    if eligible_subtotal < g.cart.get_discountable_subtotal():
        return ("9.99", 0.00)

    return (discount.get("discount"), 0.00)
