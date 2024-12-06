from datetime import datetime
from flask import g, current_app
from copy import copy
from pprint import pprint
import math
from flask_app.modules.helpers import split_to_list, format_currency
from flask_app.modules.preload import get_product_promo_values, get_categories_products


def apply_buy_x(discount=None):
    """Apply buy X get 1 free promo

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

    # found but qty threshold (discount['order_min']) is not met
    if eligible_qty < discount.get("order_min", 1):
        return None

    # sort by price low to high
    promo_items_sorted = sorted(promo_items, key=lambda d: d.get('price'))
    # current_app.logger.debug("ELIG QTY: " + str(eligible_qty))
    # current_app.logger.debug("VALID ITEMS: ")
    # for item in promo_items_sorted:
    #   current_app.logger.debug(str(item.get_item()))

    # find out how many eligible "sets" there are
    eligible_free = 1
    # buy 1 get 1 is different math than buy 2,3,4 get 1...
    if discount.get("order_min") == 1:
      eligible_free = math.floor(eligible_qty / 2)
    else:
      eligible_free = math.floor(eligible_qty / discount.get("order_min"))



    #current_app.logger.debug("ELIGIBLE SETS: " + str(eligible_free))

    # loop the cart items, then their quantities and create a table of discountable skus+quantities
    total_qty_discounted = 0
    discounted_skus = {}
    for item in promo_items_sorted:
      skuid = item.get('skuid')
      if (total_qty_discounted < eligible_free):
        for i in range(item.get('quantity')):
          if (total_qty_discounted < eligible_free):
            total_qty_discounted = total_qty_discounted + 1
            if discounted_skus.get(skuid):
              discounted_skus[skuid] = discounted_skus[skuid] + 1
            else:
              discounted_skus[skuid] = 1
          else:
            break
      else:
        break

    # current_app.logger.debug(str(discounted_skus))

    # now loop the discounted_skus dict and calculate prices
    for sku, discountable in discounted_skus.items():
      # print(f"sku, discountable {sku} , {discountable}")
      cur_item = g.cart.get_item_by_skuid(sku)
      product_price = copy(cur_item.get("price"))
      # if the item qty is > the number discountable, you have to modify the each price
      # to reflect the number of free ones
      if cur_item.get('quantity') > discountable:
        priced_qty = cur_item.get('quantity') - discountable
        new_price = product_price / priced_qty
        cur_item.set("price", new_price)
        cur_item.set("ppd1_price", product_price)
        cur_item.set("is_tweaked", True)
        printable_savings = format_currency(discountable * product_price)
        cur_item.set("promo_message", f"Item price adjusted to reflect {discountable} free. Savings: {printable_savings}")

      else:
        cur_item.set("price", 0.00)
        cur_item.set("ppd1_price", product_price)
        cur_item.set("is_tweaked", True)