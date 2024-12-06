from datetime import datetime
from flask import g, session, current_app
from copy import copy
from pprint import pprint
import math
from flask_app.modules.cart_item import CartItem
from flask_app.modules.cart.promos import apply_discount_by_type
from flask_app.modules.helpers import format_currency, is_number, split_to_list, image_path
from flask_app.modules.product import Product, get_path_by_skuid
from flask_app.modules.extensions import DB
from flask_app.modules.preload import (
  get_discounts,
  get_product_promo_values,
  get_categories_products,
  get_promo_exclusions
)
from flask_app.modules.discounts.shipping import group_min_spend_shipping_discount
from flask_app.modules.discounts.group_min_spend import group_min_spend_discount


def apply_promo_message():
    """if a coupon is applied, set a message

    Args:
      discount (dict): The discount object (loaded from 'discounts')
    """

    coupon = g.promo_code
    discounts = get_discounts()
    discount = {}

    if not coupon or not coupon in discounts["index"]:
        return None

    # create a list of excluded SKUs
    exclude_skus = get_promo_exclusions()
    discountable = 0.00
    for cart_item in g.cart.get_items():
        if CartItem.get_base_skuid(cart_item.get("skuid")) not in exclude_skus:
            discountable += cart_item.get("quantity") * cart_item.get("price", 0)

    # retrieve the potential object(s) associated with this coupon code
    # there can be multiple objects found per code because of tiered discounts
    matched = [i for i in discounts["data"] if coupon == i["code"]]

    if not len(matched):
        return None

    # if there's more than 1 found, it's a tiered discount
    if len(matched) > 1:
        # sort hi to low
        matched = sorted(matched, key=lambda k: k["order_min"], reverse=True)
        # check each tier against discountable total
        for disc in matched:
            if is_number(disc.get("discount")) and discountable >= float(disc.get("order_min")):
                discount = disc
                break
        # if none found, use the lowest tier
        if not discount:
            discount = matched[-1]

    else:
        discount = matched[0]

    if not discount:
        return None

    # check if expired

    start_time = discount.get("start_timestamp") if isinstance(discount.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
    end_time = discount.get("end_timestamp") if isinstance(discount.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

    if end_time < datetime.now():
        g.messages["promo"] = f"Coupon code {coupon} is expired"
        session["coupon_code"] = ""
        return None

    # check if not active yet
    if start_time > datetime.now():
        g.messages["promo"] = f"Coupon code {coupon} is not yet active"
        session["coupon_code"] = ""
        return None

    cached_product_promos = get_product_promo_values()
    cached_categories_products = get_categories_products()

    # if this is a $-off order-level promo, make sure the discount doesn't exceed the order total
    # (in case an order minimum was left off)
    if discount.get("discount_type") == "1":
        if is_number(discount.get("discount")) and discountable - float(discount.get("discount")) <= 0:
            g.messages[
                "promo"
            ] = f"Discount cannot exceed discountable order total.  Please add more items and re-add the coupon"
            session["coupon_code"] = ""
            return None

    # check if all items on the order are PROMO_EXCLUDE
    if all(i in exclude_skus for i in g.cart.get_base_skuids()):
        g.messages["promo"] = f"No items in your cart are eligible for a promotion"
        session["coupon_code"] = ""
        return None


    # DISCOUNT TYPE 8 - validate item-level qty threshold
    if discount.get("discount_type") == "8":
      quantity_valid = 0

      if discount["item_level_discount_type"] == "1":
        for item in g.cart.get_items():
            quantity_valid = quantity_valid + item.get('quantity')

      if discount["item_level_discount_type"] == "2":
        for item in g.cart.get_items():
          if item.get("unoptioned_skuid") in cached_product_promos["index"]:
              data = cached_product_promos["data"]
              for val in split_to_list(discount["item_level_discount_value"]):
                  f = next((i for i in data if i["skuid"] == item.get("unoptioned_skuid") and i["value"] == val), None)
                  if f:
                      quantity_valid = quantity_valid + item.get('quantity')
                      break

      if discount["item_level_discount_type"] == "3":
        valid_categories = split_to_list(discount["item_level_discount_value"])
        valid_skus = []
        for category in valid_categories:
          valid_skus.extend(cached_categories_products.get(category, []))
        for item in g.cart.get_items():
          base_skuid = CartItem.get_base_skuid(item.get("skuid"))
          if base_skuid in valid_skus:
            quantity_valid = quantity_valid + item.get('quantity')

      # check quantity valid

      # check if this is a QUANTITY tiered offer
      qty_valid = False
      for disc in matched:
          if is_number(disc.get("discount")) and quantity_valid >= int(disc.get("order_min")):
              discount = disc
              qty_valid = True
              break
      if not qty_valid:
          discount = matched[-1]

      if quantity_valid >= discount.get('order_min', 1):
        g.messages[
            "promo"
        ] = f"Coupon {discount.get('code')} has been applied: {discount.get('discount_desc')}.  Cannot be combined with other offers."
        return None
      else:
        order_min = int(discount.get("order_min", 1))
        g.messages[
            "promo"
        ] = f"The quantity minimum for {coupon} is {order_min}.  Please re-enter the coupon code when you're reached the minimum."
        session["coupon_code"] = ""
        return None

    # validate item-level promos
    if discount.get("discount_type") in ["4", "6", "7", "9"]:

      # a list of the eligible items
      promo_items = []

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
          g.messages[
              "promo"
          ] = f"Please add {int(discount.get('order_min'))} eligible item(s) to your cart, then re-add the coupon code for: {discount.get('discount_desc')}."
          session["coupon_code"] = ""
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
          g.messages[
              "promo"
          ] = f"Please add {int(discount.get('order_min'))} eligible item(s) to your cart, then re-add the coupon code for: {discount.get('discount_desc')}."
          session["coupon_code"] = ""
          return None

    # validate free gift promo
    elif discount.get("discount_type") == "5":
        if discountable < discount.get("order_min"):
            order_min = format_currency(discount.get("order_min"))
            g.messages[
                "promo"
            ] = f"The order minimum for {coupon} is {order_min}.  Please re-enter the coupon code when you're reached the minimum."
            session["coupon_code"] = ""
            return None

        # if the 'discount' value is a skuid, it's a prerequesite in the cart
        if discount.get("discount") and \
          isinstance(discount.get("discount"), str) and \
          not is_number(discount.get("discount")) and \
          len(discount.get("discount")) > 3:

          if not g.cart.get_items_by_base_skuid(discount.get("discount")):
            prereq_prod = Product.from_skuid(discount.get("discount"))
            if not prereq_prod:
              return None

            path = get_path_by_skuid(prereq_prod.get('skuid'))
            g.messages[
                "promo"
            ] = f"Please add <a href='{path}'>{prereq_prod.get('name')}</a> to your cart, then re-add the coupon code to redeem."
            session["coupon_code"] = ""
            return None

        # get cart skuids
        base_skuids = g.cart.get_base_skuids()
        cart_skuids = g.cart.get_skuids()

        # get promo skuids/products
        promo_skuids = discount["item_level_discount_value"].strip()
        promo_skuids = split_to_list(promo_skuids)
        promo_base_skuids = [CartItem.get_base_skuid(i) for i in promo_skuids]
        promo_base_skuids = list(set(promo_base_skuids))

        # current_app.logger.debug('promo_skuids {} promo_base_skuids {}'.format(promo_skuids, promo_base_skuids))

        # if there is no free gift redemption in the cart, load the list for the modal gift picker
        if not any((True for x in cart_skuids if x in promo_skuids)):
          # current_app.logger.debug('PROMO NOT IN CART')
          free_gifts = []
          for fullsku in promo_skuids:
            free_gift = {}
            my_base_sku = CartItem.get_base_skuid(fullsku)
            my_prod = Product.from_skuid(my_base_sku)
            if not my_prod:
              continue
            # pprint(my_prod.to_dict())
            free_gift["skuid"] = my_base_sku
            free_gift["fullskuid"] = fullsku if len(fullsku) > len(my_base_sku) else my_base_sku
            free_gift["name"] = my_prod.get('name', "").replace(' T-Shirt or Sweatshirt', '')
            free_gift["default_image"] = image_path(discount.get('code'))
            free_gift["image"] = image_path(my_prod.get('images', {}).get('smlimg'))
            free_gift["price"] = my_prod.get('origprice') if my_prod.get('origprice') else my_prod.get('price')

            # if the fullsku is longer than the base sku, it's an optioned product
            if len(fullsku) > len(my_base_sku):
              my_fullsku = fullsku.replace('-', '')
              opres = DB.fetch_one("SELECT * FROM options_index WHERE fullsku = %s", (my_fullsku,))
              if opres:
                free_gift["name"] = free_gift["name"] + " - " + opres.get('description').replace(';', ' - ')
                op_price_list = split_to_list(opres.get('origprice_pricechange'))
                int_list = [int(float(x)) for x in op_price_list]
                free_gift["price"] = free_gift["price"] + sum(int_list)

                # dig for a variant image
                if my_prod.get('variants_to_images'):
                  vimg = my_prod.get('variants_to_images')
                  sku_part_list = split_to_list(fullsku.replace('-',';'))
                  partbase = ""
                  for part in sku_part_list:
                    # partbase = partbase + part1
                    image_obj = next((i for i in vimg if i.get('fullskuid') == partbase), None)
                    if image_obj:
                      free_gift['image'] = image_obj.get('images', {}).get('small')
                      # current_app.logger.debug("FOUND OP IMAGE for partbase {} {}".format(partbase, free_gift['image']))
                      break

            free_gifts.append(free_gift)
            #pprint(free_gifts)
            g.prompt_free_gift = free_gifts

        else:
          # promo is in the cart.  make sure it doesn't have a qty > 1
          promo_cart_items = g.cart.get_items_by_skuid_list(promo_skuids)
          qty_over_items = next((p for p in promo_cart_items if p.get("quantity") > 1), None)
          if qty_over_items:
            g.messages[
                "promo"
            ] = f"Reduce the quantity of the promo item to 1 to get the promotional price."
            return None

        g.messages["promo"] = f"Coupon {discount.get('code')} has been applied: {discount.get('discount_desc')}. Cannot be combined with other offers."
        return None

    elif discount.get("discount_type") == "10":
      (disc_value, difference) = group_min_spend_shipping_discount(discount)
      if not disc_value:
          g.messages[
              "promo"
          ] = f"Please add {format_currency(difference)} eligible item(s) to your cart, then re-add the coupon code for: {discount.get('discount_desc')}."
          session["coupon_code"] = ""
          return None

    elif discount.get("discount_type") == "11":
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
        difference = float(discount.get("order_min", 1) - eligible_subtotal)
        g.messages[
            "promo"
        ] = f"Please add {format_currency(difference)} worth of eligible item(s) to your cart, then re-add the coupon code for: {discount.get('discount_desc')}."
        session["coupon_code"] = ""
        return None
      else:
        g.messages["promo"] = f"Coupon {discount.get('code')} has been applied: {discount.get('discount_desc')}. Cannot be combined with other offers."



    else:
        if discountable < discount.get("order_min"):
            order_min = format_currency(discount.get("order_min"))
            cost_diff = format_currency(discount.get("order_min") - discountable)
            g.messages[
                "promo"
            ] = f"Spend {cost_diff} more to get {discount.get('discount_desc')}.  Please re-enter the coupon code when you're reached {order_min}."
            session["coupon_code"] = ""
            return None

    g.messages["promo"] = f"Coupon {discount.get('code')} has been applied: {discount.get('discount_desc')}.  Cannot be combined with other offers."