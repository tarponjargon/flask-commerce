""" processes cart item tweaks.  a "tweak" allows for dynamic modification of the cart ITEM data (i.e. line-item level) """

import re
from copy import copy
from datetime import datetime
from flask import g, current_app
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import is_number, split_to_list
from flask_app.modules.preload import (
  get_discounts,
  get_product_promo_values,
  get_categories_products,
  get_promo_exclusions
)
import traceback

from flask_app.modules.http import session_get


def tweak_item(item_data):
    """Process item tweaks.  Receives item data, called before the CartItem object is instantiated

    Args:
      item_data (dict): The item_data data

    Returns:
      dict: The mutated item data dictionary
    """

    # apply any item-level coupon promtions
    coupon_promo = check_item_coupon_discount(item_data)
    if coupon_promo:
        item_data.update(coupon_promo)

    # apply any cart upsell special pricing
    cart_upsell = check_cart_upsell(item_data)
    if cart_upsell:
        item_data.update(cart_upsell)

    return item_data


def check_item_coupon_discount(item):
    """Handles item-level discounts that are triggered by coupon code.

    Args:
      item (dict): The item data dictionary

    Returns:
      dict: A dictionary containing the item keys to update
    """

    coupon = g.promo_code
    now = datetime.now()

    if not coupon:
        return {}
    else:
        coupon = coupon.upper()

    discounts = get_discounts()

    # see if an active promo exists for given coupon code
    # only handle types "4" (item price), and "6" (free item-level shipping).
    # type "7" is item-level but is handled in post-process since other cart items must be known
    discount = {}
    if coupon in discounts["index"]:
        discount = next(
            (i for i in discounts["data"] if i.get("code") == coupon and i.get("discount_type") in ["4"]),
            None,
        )

    # don't double-tweak
    if item.get("is_tweaked"):
        return False

    if not discount:
        return {}

    start_time = discount.get("start_timestamp") if isinstance(discount.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
    end_time = discount.get("end_timestamp") if isinstance(discount.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

    # if found but expired
    if start_time > now:
      current_app.logger.debug("this coupon is not yet active")
      return {}
    if end_time < now:
      current_app.logger.debug("this coupon is expired")
      return {}

    # if this sku is specifically excluded
    cached_product_promos = get_promo_exclusions()
    if item.get("unoptioned_skuid") in cached_product_promos:
        return {}

    return apply_item_level_discount(item, discount)


def apply_item_level_discount(item=None, discount=None):
    """Applies an item-level discount.  Item level discounts are denoted in the 'discounts'
    table by discount_type = '4' (item price adjustment)

    Args:
      item (dict): The item data dictionary for the item that will be discounted
      discount (dict): The discount data (derived from the discounts table) to apply

    Returns:
      dict: The updated keys to update the item dictionary with
    """

    if not item:
        item = {}
    if not discount:
        discount = {}

    new_keys = {}
    promo_valid = False

    # item_level_discount_type = '1' means all items are discounted
    if discount["item_level_discount_type"] == "1":
        promo_valid = True

    # item_level_discount_type = '2' means it's a discount with a CLEARANCE_SPECIAL value
    # This is a way to arbitrarily group item together for promotions (like all items with CLEARANCE_SPECIAL: 5)
    # there can be multiple CLEARANCE_SPECIAL values, semicolon-delimited
    if discount["item_level_discount_type"] == "2":
        cached_product_promos = get_product_promo_values()
        if item.get("unoptioned_skuid") in cached_product_promos["index"]:
            data = cached_product_promos["data"]
            for val in split_to_list(discount["item_level_discount_value"]):
                f = next((i for i in data if i["skuid"] == item.get("unoptioned_skuid") and i["value"] == val), None)
                if f:
                    promo_valid = True
                    break

    # item_level_discount_type = '3' means it's a discount on a category or group of categories
    # check sku against the index of categories->products to validate
    # there can be multiple categories specified (semicolon-delimited)
    if discount["item_level_discount_type"] == "3":

        for category in split_to_list(discount["item_level_discount_value"]):
            cached_categories_products = get_categories_products()
            skus = cached_categories_products.get(category, [])
            if item.get("unoptioned_skuid") in skus:
                promo_valid = True
                break

    # item_level_discount_type = '4' means it's a discount on a SKU(s) specified
    # in discounts.item_level_discount_value
    # there can be multiple skus specified (semicolon-delimited)
    if discount["item_level_discount_type"] == "4":
        skus = split_to_list(discount["item_level_discount_value"])
        if item.get("unoptioned_skuid") in skus:
            promo_valid = True

    # if the promo is validated, apply the discount to the price.  The 'discount' field value is a string

    if promo_valid:
        num = discount["discount"]

        # if the discount is a number and value is >1 it's a $-off discount
        if discount["discount_type"] == "4" and is_number(num) and float(num) > 1 and float(num) < item.get("price"):
            new_keys["price"] = item.get("price") - float(num)

        # the discount is a percentage (0.10), apply %-off discount
        elif discount["discount_type"] == "4" and is_number(num) and float(num) < 1 and float(num) > 0:
            new_keys["price"] = item.get("price") * (1 - float(num))

        # if the discount price has been set, set ppd1_price to the original item price
        if new_keys.get("price"):
            new_keys["ppd1_price"] = copy(item.get("price"))
            new_keys["is_tweaked"] = True

    return new_keys


def check_cart_upsell(item):
    """Check if there is cart upsell special pricing active.  The cart upsell the customer has chosen
    is in their session as SO_ACCEPT=[id]

      Args:
        item (dict): The item data dictionary

      Returns:
        dict: A dictionary containing the item keys to update
    """

    # don't double-tweak
    if item.get("is_tweaked"):
        return False

    id = session_get("SO_ACCEPT")
    if not session_get("SO_ACCEPT") or not is_number(session_get("SO_ACCEPT")):
        return {}

    new_keys = {}
    base_skuid = item.get("unoptioned_skuid")
    sql = """
      SELECT
        skuid,
        origprice+0 as origprice,
        price+0 as price,
        break_qty,
        IFNULL(break_price+0,0.00) AS break_price
      FROM cart_upsells
      WHERE id = %(id)s
      AND skuid = %(base_skuid)s
      AND start_date < NOW()
      AND end_date > NOW()
    """
    params = {"id": id, "base_skuid": base_skuid}
    upsell = DB.fetch_one(sql, params)

    if not upsell:
        return {}

    # if selling price is lower than specified upsell price, make tweak price selling price
    price = upsell.get("price") if upsell.get("price") < item.get("price") else item.get("price")
    origprice = upsell.get("origprice") if upsell.get("origprice") > item.get("origprice") else item.get("origprice")
    break_qty = upsell.get("break_qty") if price > upsell.get("break_price") else None
    break_price = (
        upsell.get("break_price") if upsell.get("break_price") > 0 and price > upsell.get("break_price") else None
    )

    # if this is an optioned item that has upcharges, add the upcharge to the price (and breakprice)
    if item.get("variant_upcharges"):
        price = price + item.get("variant_upcharges")
        if break_price:
            break_price = break_price + item.get("variant_upcharges")

    # if there is a break qty and the item qty threshold is met
    if break_qty and break_price and item.get("quantity") >= break_qty:
        price = break_price

    new_keys["price"] = price
    new_keys["ppd1_price"] = origprice
    new_keys["is_tweaked"] = True

    # print(new_keys)
    # print(traceback.print_stack())
    # print(datetime.now())
    return new_keys
