""" Cart module

An instantiated Cart class contains totals, subtotals, shipping and cart items as CartItem objects.  Generally it is
instantiated using the classmethod: Cart.from_session(), not directly
"""

from copy import deepcopy
from datetime import datetime
import json
import traceback
import re
import traceback
from flask import current_app, g, request, session
from flask_app.modules.cart_item import CartItem
from flask_app.modules.cart.shipping import get_method_descriptions
from flask_app.modules.cart.surcharge import calculate_surcharge
from flask_app.modules.extensions import DB, redis_cart
from flask_app.modules.helpers import (
    days_between,
    format_currency,
    reformat_datestring,
    sanitize,
    create_uuid,
    match_uuid,
    days_seconds,
    split_to_list,
    set_order_note,
    is_number
)
from flask_app.modules.http import session_get, get_session_id
from flask_app.modules.regions import get_tax_rate
from flask_app.modules.vertex import get_vtax_rate
from flask_app.modules.cart.tax import get_canada_tax_rate
from flask_app.modules.preload import (
  get_promo_exclusions,
  get_discounts,
  get_shipping_rates
)
from flask_app.modules.discounts.shipping import group_min_spend_shipping_discount


class Cart(object):
    def __init__(self, cart_data=None):
        if cart_data is None:
            cart_data = {}

        self.data = cart_data

    def get_id(self):
        """Gets the user's cart id.  It's possible that there isn't one, because carts only exist
        when items get added

        Returns:
          str: The cart id (a uuid)
        """
        val = request.cookies.get(current_app.config["CART_COOKIE_NAME"], None)
        return val if val and match_uuid(val) else None

    def get(self, key, default=None):
        """Generic getter for Cart data dict

        Args:
          key (str): The key to get
          default (any): The value to return if key not found

        Returns:
          any: The value for the given key
        """
        return self.data.get(key, default)

    def set(self, key, value):
        """Generic setter for Cart data dict

        Args:
          key (str): The key to add to the cart data dictionary
          value (any): the value to set
        """
        self.data[key] = value

    def get_cart(self):
        """Gets cart data as dictionary (CartItem, Product objects are retained)

        Returns:
          dict: The cart data
        """
        return self.data

    def get_items(self):
        """Gets cart items list

        Returns:
          list: A list of objects, each being a CartItem
        """
        return self.data.get("items", [])

    def get_skuids(self):
        """Gets skuids in cart as list

        Returns:
          list: A list of strings, each being a SKU in the cart.
        """
        return [i.get("skuid") for i in self.get_items()]

    def get_base_skuids(self):
        """Gets base skuids in the cart

        Returns:
          list: A list of strings, each being a base SKU in the cart.
        """
        return list(map(CartItem.get_base_skuid, self.get_skuids()))

    def to_dict(self, detail=False):
        """Convert Cart, CartItem and Product to dict

        Args:
          self (Cart): The Cart object
          detail (boolean): Whether or not to include the product object (as dict) with the CartItem

        Returns:
          dict: The cart data with associated objects converted to a dictionary
        """

        cart_dict = deepcopy(self.data)
        cart_dict["items"] = [i.to_dict(detail) for i in self.data["items"]]
        return cart_dict

    def to_json(self, detail=False):
        """Convert Cart, CartItem and Product to JSON

        Args:
          self (Cart): The Cart object
          detail (boolean): Whether or not to include the product object with the CartItem

        Returns:
          dict: The cart data with associated objects converted to JSON
        """
        cart_dict = self.to_dict(False)
        return json.dumps(cart_dict)

    def is_empty(self):
        """Method to check if the cart is empty

        Returns:
          bool: True if the cart is empty, False if it has items
        """
        return True if len(self.data["items"]) == 0 else False

    def has_autoship(self):
        """Checks if any of the CartItem objects have autoship items

        Returns:
          int: returns the number of CartItems that are autoship
        """
        autoship_items = 0
        for item in self.get_items():
          if item.is_autoship():
            autoship_items = autoship_items + 1
        return autoship_items

    def has_missing_variants(self):
        """Checks if any of the CartItem objects have missing variants

        Returns:
          CartItem: The first CartItem missing variants, or None
        """
        missing_variants = next((i for i in self.get_items() if i.is_missing_variants()), None)
        return missing_variants

    def has_missing_pers(self):
        """Checks if any of the CartItem objects have missing personalization

        Returns:
          list: A list of CartItem objects missing personalization
        """
        missing_pers = []
        for item in self.get_items():
            if item.is_missing_pers():
                missing_pers.append(item)
        return missing_pers

    def has_us_only(self):
        """Checks if any of the CartItem objects ship to US only

        Returns:
          list: A list of CartItem objects that ship to US only
        """
        us_only = []
        for item in self.get_items():
            if item.is_us_only():
                us_only.append(item)
        return us_only

    def has_lower_48_only(self):
        """Checks if any of the CartItem objects ship to continental US only

        Returns:
          list: A list of CartItem objects that ship to continental US only
        """
        lower_48_only = []
        for item in self.get_items():
            if item.is_lower_48_only():
                lower_48_only.append(item)
        return lower_48_only

    def has_institutional_edition(self):
        """Checks if any of the CartItem objects ship to continental US only

        Returns:
          list: A list of CartItem objects that ship to continental US only
        """
        institutional_edition = []
        for item in self.get_items():
            if item.is_institutional_edition():
                institutional_edition.append(item)
        return institutional_edition

    def is_club_validated(self):
        """Method to check if the customer is validated for club promotions

        Returns:
          bool: True if the customer is validated, False if not
        """
        validated = False
        for sku in current_app.config["CLUB_SKUS"]:
            if self.get_item_by_skuid(sku):
                validated = True
                break
        if session_get("BBSVALIDATED"):
            validated = True
        return validated

    def is_sample_order(self):
      """
      Method to check if the order is a sample order, meaning all of the items on the order are free samples
      Returns:
        bool: True if the order is a sample order, False if not
      """

      return all(x in current_app.config['FREE_SAMPLE_SKUIDS'] for x in self.get_base_skuids())

    def get_gc_quantities(self):
        """Gets the total quantities of gift certificates on the order

        Returns:
          int: The total quantities of gift certificates on the order
        """
        total_gcs = 0
        for item in self.get_items():
            if "C9999" in item.get("skuid"):
                total_gcs = total_gcs + item.get("quantity")
        return total_gcs

    def get_lowest_priced_items(self, how_many=1):
        """Gets the n lowest-priced items in the cart

        Args:
          how_many (int): How many items to return (default 1)

        Returns:
          list: the lowest-priced CartItems, sorted high to low price
        """
        items = self.get_items()
        if how_many > len(items):
            how_many = len(items)
        lowest_priced_items = sorted(items, key=lambda k: k["prices"]["price"])
        return lowest_priced_items[:how_many]

    def get_highest_priced_item(self, include_promo_exclusions=True):
        """Get highest priced item in the cart

        Args:
          include_promo_exclusions (bool): Whether or not to consider skus specified
          to be excluded from promotions

        Returns:
          CartItem: The highest priced item in the cart, None if no items
        """
        if self.is_empty():
            return None
        highest_priced_item = None
        prev_price = 0.00
        for item in self.get_items():
            if include_promo_exclusions and item.get("unoptioned_skuid") in get_promo_exclusions():
                continue
            current_price = item.get("price")
            if current_price > prev_price:
                highest_priced_item = item
                prev_price = current_price

        return highest_priced_item

    def get_quantities(self):
        """gets total quantities of cart items

        Returns:
          int: The total quantities of all cart items (lineitems + each quantities)
        """

        return sum(i.get("quantity") for i in self.data["items"])

    def is_paypal_eligible(self):
        """Determines if the cart is eligible to be paid for with paypal

        Returns:
          bool: True if eligibile for paypal, False if not
        """
        paypal_eligible = True
        for item in self.get_items():
          if item.is_autoship():
            paypal_eligible = False
          product = item.get("product", {})
          if product.get("drop_ship") or product.get("preorder") or product.get("no_paypal"):
              paypal_eligible = False

          # not paypal eligible if backorder and days until ship > 20 days
          if product.get("backorder"):
              bo_date = reformat_datestring(product.get("backorder"))
              now = datetime.now().strftime("%Y%m%d")
              days_until_ship = days_between(now, bo_date)
              if days_until_ship > 20:
                  paypal_eligible = False

        return paypal_eligible

    def get_giftwrap_item(self):
        """Gets the giftwrap item (if exists) from the cart items

        Returns:
          CartItem: The giftwrap item (if found) or None
        """

        return next((d for d in self.get_items() if d.is_giftwrap()), None)

    def has_drop_ship(self):
        """Determines if any items on the order are drop-ship

        Returns:
          bool: True if any items are drop-ship, False if none are
        """
        return any((True for x in self.get_items() if x.get("product", {}).get("drop_ship")))

    def has_slapper(self):
        """Determines if any items on the order are "slapper"
        (not exactly sure what it is, but I think it has to do with large, heavy or drop-ship items)

        Returns:
          bool: True if any items are slapper, False if none are
        """
        return any((True for x in self.get_items() if x.get("product", {}).get("slapper")))

    def get_promo(self):
        """Gets a promotion associated with a coupon code.  Does not actually do the redemption.
        Returns an object that can be used for redemption
        NOTE: messaging is handled in post_process.apply_promo_message

        Returns:
          dict: If a valid promo is found the the order meets any hurdles,
            the discount (as loaded from 'discounts' table) is returned
        """
        coupon = g.promo_code
        promo = {}
        if coupon is None:
            return promo
        else:
            coupon = coupon.upper()

        cart_items = self.get_items()

        # contains all discounts listed in 'discounts' table (already loaded into g in before_request)
        discounts = get_discounts()

        if coupon in discounts["index"]:
            # retrieve the potential object(s) associated with this coupon code
            # there can be multiple objects found per code because of tiered discounts
            discount_obj = [i for i in discounts["data"] if coupon == i["code"]]

            # for tiered discount handling, sort potential discounts descending so that
            # the higher tiers (more valuable) are checked first
            if len(discount_obj) > 1:
                discount_obj = sorted(discount_obj, key=lambda k: k["order_min"], reverse=True)

            for obj in discount_obj:
                # create promo dict, keys are a specified subset of 'discounts' table column names
                keys = [
                    "code",
                    "discount_type",
                    "item_level_discount_type",
                    "item_level_discount_value",
                    "discount",
                    "discount_desc",
                    "order_min",
                ]
                promo = {k: v for (k, v) in obj.items() if k in keys}
                promo["valid"] = False
                promo["error"] = ""

                # special handling for free item promos
                # if the item is in the cart and has a price, it has to be excluded
                # from the subtotal for hurdle purposes
                exclude_skus = get_promo_exclusions()
                if obj["discount"] == "FREE" and obj["item_level_discount_value"]:
                    exclude_skus.update(split_to_list(obj["item_level_discount_value"]))

                # gnerate a temp subtotal for min-order "hurdle" promos
                subtotal = 0.00
                for cart_item in cart_items:
                    if CartItem.get_base_skuid(cart_item.get("skuid")) not in exclude_skus:
                        subtotal += cart_item.get("quantity") * cart_item.get("price", 0)

                # check if expired
                start_time = obj.get("start_timestamp") if isinstance(obj.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
                end_time = obj.get("end_timestamp") if isinstance(obj.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

                if end_time < datetime.now():
                    promo["error"] = f"Coupon code {coupon} is expired"

                # check if not active yet
                elif start_time > datetime.now():
                    promo["error"] = f"Coupon code {coupon} is not yet active"

                # check if order min not met
                elif subtotal < obj["order_min"]:
                    order_min = format_currency(obj["order_min"])
                    promo["error"] = f"The order minimum for {coupon} is {order_min}"

                else:  # looks good to go
                    promo["valid"] = True
                    break

        # no discount found, populate promo object with basic data
        else:
            promo["code"] = coupon
            promo["valid"] = False
            promo["error"] = f"Coupon {coupon} is not found"

        return promo

    def get_extra_shipping_cost(self):
        """Totals and extra shipping costs for items in the cart

        Returns:
          float: A total of all the extra shipping costs
        """

        add_shipping = 0.00
        for item in self.get("items"):
            # get a total of any extra-shipping fees on items.  'shipping' is a string
            add_shipping += float(re.sub("[^0-9,.]", "", item.get("shipping"))) if item.get("shipping") else 0.00

        return round(add_shipping, 2)

    def get_shipping_subtotal(self):
        """a subtotal of item prices that doesn't include shipped-free items

        Returns:
          float: Total cost applicable to shipping chart
        """

        non_shipped_free_subtotal = 0.00
        for item in self.get("items"):
            non_shipped_free_subtotal += (
                (item.get("quantity") * item.get("price", 0)) if (item.get("shipping") != "+0") else 0.00
            )

        return round(non_shipped_free_subtotal, 2)

    def get_shipping_methods(self):
        """creates a matrix of all methods and their associated costs (according to the chart) for the current order total

        Returns:
          list: A list of dictionaries, each being a shipping method
        """
        methods = []
        non_shipped_free_subtotal = self.get_shipping_subtotal()
        add_shipping = self.get_extra_shipping_cost()
        default_method = current_app.config["SESSION_DEFAULTS"]["ship_method"]
        promo = self.get_promo()

        translations = get_method_descriptions()
        shipping_rates = get_shipping_rates()

        # if AK or HI shipping state, add extra fee
        if session_get("ship_state") in ["AK", "HI"]:
            add_shipping += current_app.config["AK_HI_SURCHARGE"]

        # create dict with ship methods as keys, costs as values
        # 5/30/24 for mystery reasons the iterator has been failing in some corner case.  adding some error handling,
        # logging and fallbacks to prevent the whole thing from crashing
        # possibly re-write this as a standard loop and not a generator
        # 6/20/24 FOUND ISSUE!  It was the output of get_shipping_subtotal being a decimal like 24.990000000002 and
        # falling between the 24.99 and 25.00 tiers.  I added a round() to the output of get_shipping_subtotal
        rate_object = {}
        rate_object_error = False
        try:
          rate_object = next(
              i
              for i in shipping_rates
              if i["order_max"] >= non_shipped_free_subtotal and i["order_min"] <= non_shipped_free_subtotal
          )
        except StopIteration as e:
          rate_object_error = True
          current_app.logger.error("StopIteration error encountered.\nshipping_rates: {} \nnon_shipped_free_subtotal: {} \ntranslations: {} \nerror: {}".format(shipping_rates, non_shipped_free_subtotal, translations, e))
          current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
          current_app.logger.info("CART:\n {}".format(self.to_dict()))

        # current_app.logger.debug("RATE OBJECT {} for subtotal {}".format(rate_object, non_shipped_free_subtotal))

        # this is the fallback - hit DB directly and get rates.
        if rate_object_error:
          current_app.logger.info("RATE OBJECT ERROR - FALLING BACK TO DB")
          res = DB.fetch_one("""
            SELECT * FROM standard_rates_loop
            WHERE order_min <= %(subtotal)s
            AND order_max >= %(subtotal)s
            ORDER BY order_min DESC
          """, {"subtotal": non_shipped_free_subtotal})

          if res and res.get("shipping_cost"):
            rate_object = res
            current_app.logger.info("fallback rate object generated {} for subtotal {}".format(rate_object, non_shipped_free_subtotal))

        ship_method_costs = {}
        try:
          for m in translations:
              key = m.get("ship_method_key")
              code = m.get("ship_method_code")
              rate = rate_object[key]
              ship_method_costs[code] = rate
        except Exception as e:
          current_app.logger.error("Error encountered while creating ship_method_costs dict.  Error: {}".format(e))
          current_app.logger.error("Stack trace:\n%s", traceback.format_exc())

        # for m in translations:
        #     key = m.get("ship_method_key")
        #     code = m.get("ship_method_code")
        #     rate = rate_object[key]
        #     ship_method_costs[code] = rate

        # add on any additional shipping costs to each method
        ship_method_costs = {k: v + add_shipping for k, v in ship_method_costs.items()}

        methods = deepcopy(translations)
        for i, v in enumerate(translations):
            code = v.get("ship_method_code")
            methods[i]["ship_method_cost"] = ship_method_costs.get(code)

        # apply type 3 discount discount (or free) shipping
        if promo and promo.get("valid") and promo.get("discount_type") == "3":
            # find index of the default method
            x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
            if x > -1:
                # the discount value IS the shipping cost
                methods[x]["ship_method_cost"] = float(promo.get("discount")) + add_shipping

        # apply type "10" discount - Free/flat shipping on min spend from item group
        if promo and promo.get("valid") and promo.get("discount_type") == "10":
            (disc_value, difference) = group_min_spend_shipping_discount(promo)
            if disc_value and is_number(disc_value):
              # find index of the default method
              x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
              if x > -1:
                  # the discount value IS the shipping cost
                  methods[x]["ship_method_cost"] = float(disc_value) + add_shipping

        # custom SP promo - if all items on order are autoship, flat shipping fee of 4.95
        if current_app.config["STORE_CODE"] == 'supportplus2':
          autoship_items = g.cart.has_autoship()
          if autoship_items and autoship_items > 1 and autoship_items == len(g.cart.get_items()):
            x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
            if x > -1:
              if methods[x]["ship_method_cost"] > 4.95: # do not apply if the shipping is already lower
                methods[x]["ship_method_cost"] = 4.95 + add_shipping

        # if this is a club membership, give free standard shipping
        if current_app.config["STORE_CODE"] == 'basbleu2' and self.is_club_validated():
            x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
            if x > -1:
              methods[x]["ship_method_cost"] = 0.00 + add_shipping

        # custom PBS - 9.99 shipping on each QTY of institiutional edition items
        if current_app.config["STORE_CODE"] == 'pbs2' and self.has_institutional_edition():
          inst_items = self.has_institutional_edition()
          inst_qty = sum([i.get("quantity") for i in inst_items])
          x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
          if x > -1:
            methods[x]["ship_method_cost"] = (9.99 * inst_qty) + add_shipping

        # check if free shipping employee code is active
        code = session_get("source_code", session_get("coupon_code"))
        if code:
            code = code.upper()
            empcodes = [i["code"] for i in current_app.config["EMPLOYEE_DISCOUNTS"] if i["code"] != "EMPSHIP"]
            if code in empcodes:
                # find index of the default method
                x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
                if x > -1:
                    # the discount value IS the shipping cost
                    methods[x]["ship_method_cost"] = 0.00

        # if the cart has a drop-ship item, only show the default method
        if self.has_drop_ship():
            x = next((i for (i, d) in enumerate(methods) if d["ship_method_code"] == default_method), -1)
            if x > -1:
                methods = [methods[x]]

        return methods

    def get_selected_shipping_method(self):
        """Gets the shipping method object (name, cost, desc, etc) for the currently-selected shipping method
        Based on the cart total/shipping chart

        Returns:
          dict: the shipping method object (name, cost, desc, etc) for the selected shipping method
        """

        default_code = current_app.config["SESSION_DEFAULTS"]["ship_method"]
        methods = self.get_shipping_methods()
        method = session_get("ship_method", default_code)
        method_object = next((m for m in methods if m.get("ship_method_code") == method), None)

        # if nothing found, possibly a bad code was passed on the url, find the object for the default ship method
        if not method_object:
            method_object = next((m for m in methods if m.get("ship_method_code") == default_code), None)

        if not method_object:
            # this really should not happen.  if it does I am going to just report it and return the chart cost
            shipping_cost = 8.99
            subtotal = self.get_subtotal()
            res = DB.fetch_one("""
              SELECT shipping_cost
              FROM standard_rates_loop
              WHERE order_min <= %(subtotal)s
              AND order_max >= %(subtotal)s
              ORDER BY order_min DESC""",
            {"subtotal": subtotal})
            if res and res.get("shipping_cost"):
              shipping_cost = res.get("shipping_cost")
            method_object = {
                "ship_method_code": default_code,
                "ship_method_name": "Standard",
                "ship_method_cost": shipping_cost,
                "ship_method_desc": "Standard Shipping",
            }
            current_app.logger.error("Could not find shipping method object the normal way, returning chart object {}".format(method_object))

        return method_object

    def get_express_rates(self):
        """Gets the express shipping base rates. This is found in the 0.00 tier of the shipping object (chart)

        Returns:
          dict: A dictionary containing the rates

          example: {
                "rush": 9.99,
                "2day": 11.99,
                "overnight": 20.99,
                "canada": 24.99
          }
        """

        rates = get_shipping_rates()
        base = next((i for i in rates if i["order_min"] == 0.00), None)
        return {
            "rush": base["rush"] if "rush" in base else 99.99,
            "2day": base["2day"] if "2day" in base else 99.99,
            "overnight": base["overnight"] if "overnight" in base else 99.99,
            "canada": base["canada"] if "canada" in base else 99.99,
        }
    def get_club_savings(self):
      """ Gets the total savings from club membership.  Merely "sugar" data that exists only in the UI

        Returns:
          float: The total savings from club membership
      """

      item_savings = 0.00
      shipping_savings = 0.00

      # calculate club savings on items
      for item in self.get_items():
        clubprice = float(item.get("product", {}).get("bbsdiscount", 0.00))
        productprice = float(item.get("product", {}).get("pristine_price", 0.00))
        if clubprice and productprice and clubprice < productprice:
          item_savings += productprice - clubprice

      # calculate club savings on shipping
      non_shipped_free_subtotal = self.get_shipping_subtotal()
      rates = get_shipping_rates()
      rate_object = next(
          i
          for i in rates
          if i["order_max"] >= non_shipped_free_subtotal and i["order_min"] <= non_shipped_free_subtotal
      )
      if rate_object and rate_object.get("shipping_cost", 0.00):
        shipping_savings = rate_object.get("shipping_cost", 0.00)

      # current_app.logger.debug("club savings on items: [{}]".format(item_savings))
      # current_app.logger.debug("shipping savings on items: [{}]".format(shipping_savings))
      return round(item_savings + shipping_savings, 2)

    def get_subtotal(self, skip_nontax=False):
        """Gets the cart subtotal BEFORE any order-level discount

        Args:
          skip_nontax (bool): Skip nontaxable items

        Returns:
          float: The cart subtotal
        """
        nontaxable_items = session_get("nontaxable_items", [])
        subtotal = 0.00
        for item in self.data["items"]:
            if skip_nontax and (item.get("skuid") in nontaxable_items):
                continue
            subtotal += item.get("quantity") * item.get("price", 0)

        subtotal = round(subtotal, 2)
        return subtotal

    def get_discountable_subtotal(self):
        """Gets the cart subtotal BEFORE any order-level discount
        excludes the total prices of any items not eligible to be discounted
        I am using 'C9999' to catch gift certificates

        Returns:
          float: The discountable cart subtotal
        """
        subtotal = 0.00
        exclude_skus = get_promo_exclusions()
        for item in self.data["items"]:
            if "C9999" in item.get("skuid") or item.get("unoptioned_skuid") in exclude_skus:
                continue
            subtotal += item.get("quantity") * item.get("price", 0)

        subtotal = round(subtotal, 2)
        return subtotal

    def get_customer_discount(self):
        """Gets any order-level discount applied for advertised promotion
        (discount_type 1 or 2 in the 'discounts' table)

        Returns:
          float: The discount value
        """
        discount = 0.00
        promo = self.get_promo()
        subtotal = self.get_discountable_subtotal()

        # 1= dollar off, 2=% off. the only types handled by this function
        discount_types = ("1", "2")

        # only do discount calcs if there's a discount found and it's type 1 or 2 ($-off or %-off)
        if promo and promo.get("valid") and promo.get("discount_type") in discount_types:
            promo_discount = float(promo.get("discount"))
            order_min = promo.get("order_min", 0.00)

            # discount_type = 1 : the discount price is stated directly (dollar off)
            if (
                promo.get("discount_type") == "1"
                and subtotal >= order_min
                and promo_discount > 1
                and promo_discount < subtotal
            ):
                discount = promo_discount

            # discount_type = 2 : % off
            elif (
                promo.get("discount_type") == "2"
                and subtotal >= order_min
                and promo_discount < 1
                and promo_discount > 0
            ):
                discount = subtotal * promo_discount
        discount = round(discount, 2)

        return discount

    def get_employee_discount(self):
        discount = 0.00
        subtotal = self.get_discountable_subtotal()

        # if the discount is an employee discount, it is applied as normal (in the cart)
        # BUT some of the codes need to have the shipping address forced
        code = session_get("source_code", session_get("coupon_code"))
        if code:
            code = code.upper()
            source_codes = [i["code"] for i in current_app.config["EMPLOYEE_DISCOUNTS"]]
            if code in source_codes:
                discount = subtotal * 0.40

        discount = round(discount, 2)
        return discount

    def get_discount(self):
        """Gets the total order-level discount appied by adding any customer
        discount and employee discount values

        Returns:
          float: The discount value
        """
        customer_discount = self.get_customer_discount()
        employee_discount = self.get_employee_discount()
        discount = customer_discount + employee_discount
        discount = round(discount, 2)
        return discount

    def get_discounted(self, skip_nontax=False):
        """Gets the cart subtotal AFTER any order-level discount

        Args:
          skip_nontax (bool): Skip nontaxable items during subtotal calculation

        Returns:
          float: The cart subtotal after discount is applied
        """
        subtotal = self.get_subtotal(skip_nontax)
        discounted = subtotal - self.get_discount()
        total = discounted if discounted > 0 else subtotal
        total = round(total, 2)
        return total

    def get_shipping(self):
        """Gets the shipping cost for the selected shipping method (or default)

        Returns:
          float: The shipping cost
        """
        methods = self.get_shipping_methods()
        # make sure ship methid is valid (it can be passed in as param), if not set to default
        valid_code_list = [i.get("ship_method_code") for i in methods]
        if not session.get("ship_method") in valid_code_list:
            session["ship_method"] = current_app.config["SESSION_DEFAULTS"]["ship_method"]
        method = session.get("ship_method")
        cost = next((m.get("ship_method_cost") for m in methods if m.get("ship_method_code") == method), 0.00)

        cost = round(cost, 2)
        return cost

    def get_tax(self):
        """Gets the total tax for the selected tax region

        Returns:
          float: The tax cost
        """
        tax = 0.00

        if session.get("ship_country") == "USA" and session.get("ship_postal_code"):
            skuid_items = [item.get("skuid") for item in g.cart.get_items()]
            skuids_in_cart = ",".join(skuid_items)
            shipping_as_string = str(self.get_shipping())
            addr_cache_key = (
                session_get("ship_street", "")
                + " "
                + session_get("ship_street2", "")
                + " "
                + session_get("ship_city", "")
                + " "
                + session_get("ship_state")
                + " "
                + session_get("ship_postal_code", "")
                + " "
                + session_get("ship_country", "")
                + " "
                + skuids_in_cart
                + " "
                + shipping_as_string
            )
            tax_obj = get_vtax_rate(addr_cache_key)
            current_app.logger.debug(tax_obj)
            if tax_obj is None:
                current_app.logger.error("vertex lookup failed -- using get_tax_rate fallback")
                tax_obj = get_tax_rate(session.get("ship_postal_code"))
                current_app.logger.debug(tax_obj)
            if not tax_obj:
                tax_obj = {}
            if tax_obj.get("shipping_taxable"):
                tax = float(tax_obj.get("rate", 0)) * (self.get_discounted(True) + self.get_shipping())
            else:
                tax = float(tax_obj.get("rate", 0)) * self.get_discounted(True)

        if session.get("ship_country") == "CANADA" and session.get("ship_state"):
          canada_tax_rate = get_canada_tax_rate(session_get("ship_state"))

          if canada_tax_rate > 0:
            tax = self.get_discounted() * canada_tax_rate
            current_app.logger.debug("CANADA TAX RATE: {}".format(canada_tax_rate))
            current_app.logger.debug("CANADA TAX: {}".format(tax))
            set_order_note("Canadian tax has been estimated for this order")

        tax = round(tax, 2)
        current_app.logger.debug("calc tax amt: [{}]".format(tax))
        return tax

    def get_surcharge(self):
        """Gets any final order surcharges for this order

        Returns:
          float: The surcharge
        """

        subtotal = self.get_discounted()
        surcharge = calculate_surcharge(subtotal)

        return round(surcharge, 2)

    def get_credit(self):
        """Gets the total credit to apply to the cart (example, a gift certificate)
        applied AFTER tax and shipping

        Returns:
          float: The credit amount
        """
        credit = 0.00
        running_total = self.get_discounted() + self.get_shipping() + self.get_tax() + self.get_surcharge()

        if session_get("giftcertificate") and session_get("gc_amt"):
            gc = session_get("giftcertificate")
            gc_leftover_value = 0.00
            gc_order_note = ""
            gc = re.sub(r"\W+", "", session_get("giftcertificate")) if session_get("giftcertificate") else None
            gc_amt = re.sub("[^0-9^.]", "", session_get("gc_amt")) if session_get("gc_amt") else None

            if not gc or not re.match(r"^[0-9a-zA-Z]{8,}", gc) or not gc_amt or not re.match(r"^\d*[.]?\d*$", gc_amt):
                return 0.00

            # if this is a PBS code, capture the last 9 chars
            match = re.search(r"^([8][08][0][1][1][7])([0-9A-Za-z]{9})$", gc)
            if match and match.groups and len(match.groups()):
                gc = match.group(1)

            sql = """
              SELECT gc_value
              FROM gc_status
              WHERE gc_code = %(gc)s
              AND gc_status = 'O'
              AND gc_value =  %(gc_amt)s
              AND division =  %(division)s
              LIMIT 1
            """
            params = {"gc": gc, "gc_amt": gc_amt, "division": current_app.config["DIVISION"]}
            res = DB.fetch_one(sql, params)
            if res and "gc_value" in res and res["gc_value"] > 0:
                credit = res["gc_value"]
            else:
                return 0.00

            # if the value of the gc exceed that of the order, note to customer there will be a refund,
            # set the gc value to the running total so that order total will be 0 and not a negative number
            if credit > running_total:
                gc_leftover_value = credit - running_total
                credit = running_total
                gc_order_note = format_currency(gc_leftover_value) + " will be refunded"
            else:
                gc_order_note = format_currency(credit) + " credited to your order"

            set_order_note(gc_order_note)

        credit = round(credit, 2)

        return credit

    def get_total(self):
        """Gets the cart total after discount, tax and credit are applied

        Returns:
          float: The final cart total
        """
        discounted = self.get_discounted()
        shipping = self.get_shipping()
        tax = self.get_tax()
        surcharge = self.get_surcharge()
        credit = self.get_credit()
        total = (discounted + tax + shipping + surcharge) - credit

        # should obviously not happen
        if total < 0:
            total = 0.00

        return round(total, 2)

    def get_item_by_skuid(self, skuid, default=None):
        """Find a cart item with given skuid

        Args:
          skuid (str): The fully-optioned SKUID string
          default (any): The value to return if the given skuid is not in the cart

        Returns:
          CartItem: the matched item, else None
        """
        return next((p for p in self.data["items"] if p.get("skuid") == skuid), default)

    def get_items_by_skuid_list(self, skulist=None):
        """Get cart items that whose SKUs are in the given list

        Args:
          skulist (list):

        Returns:
          list: A list of CartItem objects
        """
        if skulist is None:
            skulist = []
        return [p for p in self.data["items"] if p.get("skuid") in skulist]

    def get_items_by_base_skuid(self, base_skuid):
        """Find cart items with given base SKUID

        Args:
          skuid (str): The base skuid

        Returns:
          list: A list of CartItem objects
        """
        return [p for p in self.data["items"] if p.get("unoptioned_skuid") == base_skuid]

    def get_item_index_by_skuid(self, skuid):
        """Find a cart item's index with given skuid

        Args:
          skuid (str): The fully-optioned SKUID string

        Returns:
          int: the index of the matched item, else -1
        """
        return next((i for (i, p) in enumerate(self.data["items"]) if p.get("skuid") == skuid), -1)

    def get_last_added(self):
        """Get the last added item to the cart (the first in the list)

        Args:
          none

        Returns:
          CartItem: The CartItem object last added to the cart, None if empty
        """
        last_added = { 'product': {} }
        if len(self.data["items"]):
            last_added = self.data["items"][0]
        return last_added

    def add_item(self, cart_item=None):
        """Add a CartItem to the cart if it doesn't exist.  Update it if it does.

        Args:
          cart_item (CartItem): The cart item object to add

        Returns:
          CartItem: The added or updated CartItem object
        """
        if not cart_item or not isinstance(cart_item, CartItem):
            if "not available" not in (" ").join(g.messages["errors"]):
              g.messages["errors"].append(f"Product not found.")
            g.messages["errors"].append(f"Please call {current_app.config['STORE_PHONE']} if you have any questions.")
            return None

        if (len(self.get_items()) >= current_app.config['LINEITEM_LIMIT']):
            g.messages["errors"].append(f"Limit of {current_app.config['LINEITEM_LIMIT']} cart items reached.  Please complete this order and place another.")
            current_app.logger.info(f"Limit of {current_app.config['LINEITEM_LIMIT']} cart items reached")
            return None

        # check if item already exists in cart, create a new. merge item and remove the old one
        # TODO: refactor this so it makes more sense.
        existing_item = self.get_item_by_skuid(cart_item.get("skuid"))

        if existing_item:
            merged_item = deepcopy(existing_item)
            merged_item.set("quantity", cart_item.get("quantity"))
            merged_item.set("price", cart_item.get("price"))
            if cart_item.get("personalization"):
                merged_item.set("personalization", cart_item.get("personalization"))
            cart_item = merged_item

            # report any qty change to messages
            if merged_item.get("quantity") > existing_item.get("quantity"):
                qty_change = merged_item.get("quantity") - existing_item.get("quantity")
                google_item = cart_item.get_google_object()
                google_item["quantity"] = qty_change
                g.messages["added"].append(google_item)
                g.messages["updated"].append({"item": cart_item.get_google_object(), "change": qty_change})
            else:
                qty_change = existing_item.get("quantity") - merged_item.get("quantity")
                google_item = cart_item.get_google_object()
                google_item["quantity"] = qty_change
                g.messages["removed"].append(google_item)
                g.messages["updated"].append({"item": cart_item.get_google_object(), "change": qty_change})

            # remove the old one
            # self.remove_item(existing_item.get("skuid"))
            self.data["items"] = [x for x in self.data["items"] if x.get("skuid") != existing_item.get("skuid")]
        else:
            g.messages["added"].append(cart_item.get_google_object())

        self.data["items"].insert(0, cart_item)

        return cart_item

    def remove_item(self, skuid):
        """Removes a CartItem from the cart

        Args:
          skuid (str): The fully-optioned SKUID string of the item to be removed from the cart

        Returns:
          None
        """
        current_app.logger.debug("remove " + skuid)

        cart_item = self.get_item_by_skuid(skuid)

        if cart_item:
            # update the cart items list with new list that doesn't contain the sku
            self.data["items"] = [x for x in self.data["items"] if x.get("skuid") != cart_item.get("skuid")]
            g.messages["success"].append(f"{sanitize(cart_item.get('name'))} removed from cart")
            g.messages["removed"].append(cart_item.get_google_object())
        else:
            g.messages["errors"].append(f"{sanitize(skuid)} not found in cart")

        return None

    def remove_all_items(self):
        """Removes all items from the cart.

        Returns:
          None
        """

        self.data["items"] = []

        return None

    @staticmethod
    def load_cart_from_redis(cart_id):
        """Loads cart json from redis

        Args:
          cart_id (str): The cart_id (a uuid)
        Returns:
          str: The cart retrieved from redis as JSON, or None
        """

        cart_json = None
        if cart_id and match_uuid(cart_id):
            cart_json = redis_cart.get(cart_id)

        return cart_json

    @staticmethod
    def save_cart(cart_id):
        """If the cart is not empty, persist by setting the contents to redis and the cart_id to cookie

        Args:
          cart_id (str): The cart id (a uuid).  If none, generate a new one as default

        Returns:
          str: the cart_id (a uuid)
        """
        if not cart_id or not match_uuid(cart_id):
            cart_id = create_uuid()
            # print("created cart_id", cart_id)

        # print(g.cart.to_json(False))
        cart_json = ""
        try:
            cart_json = g.cart.to_json(False)
        except Exception as e:
            current_app.logger.error(f"Error converting cart to json: {e}")

        if not cart_json:
          return ""

        if len(cart_json) > current_app.config["MAX_CONTENT_LENGTH"]:
            current_app.logger.error("Cart JSON too large to save to redis: {}".format(len(cart_json)))
            return ""

        redis_cart.set(cart_id, cart_json)
        return cart_id

    @staticmethod
    def delete_cart(cart_id):
        """Delete the cart with given ID from redis store

        Args:
          cart_id (str): The ID of the cart to delete (a uuid)

        Returns:
          int: 1 for success 0 for fail
        """
        if not cart_id or not match_uuid(cart_id):
            return None
        return redis_cart.delete(cart_id)

    @staticmethod
    def persist_cart(response):
        """Saves the cart (if not empty) and sets a cookie.  If cart has been emptied, deletes the cart and cookie

        Args:
          response (response): The Flask response object

        Returns:
          response: The Flask response object with cart_id cookie changes
        """
        # persist cart to redis if it has items, set id to cookie
        if 'cart' in g and not g.cart.is_empty() and request.path not in ["/forgetme"]:
            cart_id = Cart.save_cart(request.cookies.get(current_app.config["CART_COOKIE_NAME"]))
            if cart_id:
              expires = days_seconds(current_app.config["CART_MAX_AGE"])
              response.set_cookie(
                  current_app.config["CART_COOKIE_NAME"],
                  cart_id,
                  max_age=expires,
                  secure=True,
                  httponly=True,
                  samesite="Lax",
              )
        else:
            # cart existed but has been emptied, delete cookie and redis object
            if request.cookies.get(current_app.config["CART_COOKIE_NAME"]):
                cart_id = Cart.delete_cart(request.cookies.get(current_app.config["CART_COOKIE_NAME"]))
                response.set_cookie(
                    current_app.config["CART_COOKIE_NAME"],
                    value="",
                    max_age=0,
                    secure=True,
                    httponly=True,
                    samesite="Lax",
                )

        return response

    @classmethod
    def from_json(cls, cart_json=None):
        """Loads the cart from a JSON object (usually from the session)

        Args:
          cart_json (str): The cart json to load

        Returns:
          Cart: The instantiated Cart object
        """
        cart = {"items": []}
        if cart_json:
            cart_dict = None
            try:
              cart_dict = json.loads(cart_json)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error decoding cart: {e}")
            except ValueError as e:
                print(f"ValueError decoding cart: {e}")
            except TypeError as e:
                print(f"TypeError decoding cart: {e}")
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError decoding cart: {e}")
            except AttributeError as e:
                print(f"AttributeError decoding cart: {e}")

            if cart_dict and "items" in cart_dict:
                for item in cart_dict["items"]:
                    cart_item = CartItem.from_dict(item)
                    if cart_item:
                        cart["items"].append(cart_item)

        cart["timestamp"] = datetime.now().strftime("%Y%m%d%H%M%S")
        cart["last_session"] = get_session_id()
        return cls(cart)
