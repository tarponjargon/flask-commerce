""" CartItem module

An instantiated CartItem class contains the fully-optioned SKUID, price quantity, any personalization
data, and a reference to the associated base product object
"""

import json
import re
from pprint import pprint
from flask import current_app, g
from flask_app.modules.cart_item.availability import get_availability
from flask_app.modules.cart_item.tweak import tweak_item
from flask_app.modules.helpers import is_number, sanitize, image_path, validate_skuid
from flask_app.modules.product import Product
from flask_app.modules.category.categories import get_breadcrumb_string
from flask_app.modules.cart_item.variants import (
    get_variant_ref_list,
    get_selected_variant_data,
    check_optioned_available,
)
from flask_app.modules.extensions import DB


class CartItem(object):
    def __init__(self, cart_item=None):
        if cart_item is None:
            cart_item = {}

        self.data = cart_item

    def get_item(self, include_product=True):
        """Gets the CartItem object as dictionary.  If included, Product is kept as an object

        Args:
          include_product (boolean): Whether or not to include the associated Product object.  Default True

        Returns:
          dict: The cart item
        """
        if include_product:
            return self.data
        else:
            return {i: self.data[i] for i in self.data if i != "product"}

    def get(self, key, default=None):
        """Generic getter for CartItem data dict

        Args:
          key (str): The key to get
          default (any): The value to return if key not found

        Returns:
          any: The value for the given key
        """
        returnval = self.data.get(key)
        # do not check for falsyness for prices
        if key == 'price':
          return returnval
        return returnval if returnval else default

    def set(self, key, value):
        """Generic setter for CartItem data dict

        Args:
          key (str): The key to add to the cart item data dictionary
          value (any): the value to set
        """
        self.data[key] = value

    def get_total_price(self):
        """calculates total price for lineitem, price * quantity

        Returns:
          float: The total price for the lineitem
        """

        return self.get("price", 0) * self.get("quantity")

    def get_origprice(self):
        """calculates original price using origprice + variant upcharges
        will only calculate if the item has an origprice set

        2024-04-24: added variant_origprice_upcharges.  If this exists, it will be added to the origprice and returned

        Returns:
          float: The total original price for the lineitem
        """
        if self.get("origprice", 0.00) > 0.00 and self.get("variant_origprice_upcharges", 0.00) > 0.00:
          return self.get("origprice", 0.00) + self.get("variant_origprice_upcharges", 0.00)
        if self.get("origprice", 0.00) > 0.00:
          return self.get("origprice", 0.00) + self.get("variant_upcharges", 0.00)

        return 0.00

    def to_dict(self, include_product=True):
        """Gets CartItem object as dictionary, optionally converting any Product object to dict

        Args:
          self (CartItem): The CartItem object
          include_product (boolean): Whether or not to include the associated Product object (as dict).  Default True

        Returns:
          dict: The cart item as dict, with product object converted to dict
        """
        cart_item = {i: self.data[i] for i in self.data if i != "product"}
        if include_product:
            cart_item["product"] = self.data["product"].get_product()

        # current_app.logger.debug(cart_item)
        return cart_item

    def to_json(self, include_product=False):
        """Gets CartItem object as JSON, optionally converting any Product object to JSON

        Args:
          include_product (boolean): Whether or not to include the associated product data.  Default False
        """
        return json.dumps(self.to_dict(include_product))

    def is_missing_variants(self):
        """Checks if the associated product has variants, and if so, that the item has all variants selected

        Returns:
          bool: True if the item is missing any variants, False if it's not
        """
        if len(self.get("variant_codes", [])) < len(self.get("product", {}).get("variant_sets", [])):
            return True

        return False

    def is_giftwrap(self):
        """Checks if this item is a giftwrap (or bag)

        Returns:
          bool: True if the item is gift wrap False if it's not
        """
        val = self.get("product", {}).get("is_giftwrap")
        is_gw = True if val else False
        return is_gw

    def is_us_only(self):
        """Checks if this item is US shipping only

        Returns:
          bool: True if the item is US shipping only, False if it's not
        """
        val = self.get("product", {}).get("us_shipping_only")
        is_us_only = True if val else False
        return is_us_only

    def is_lower_48_only(self):
        """Checks if this item is restricted to continental US only

        Returns:
          bool: True if the item is continental US only, False if it's not
        """
        val = self.get("product", {}).get("restrict_ship")
        is_restrict_ship = True if val else False
        return is_restrict_ship

    def is_institutional_edition(self):
        """Checks if this item is an institiutional edition (generally for PBS only)

        Returns:
          bool: True if the item is institiutional edition, False if it's not
        """
        val = self.get("product", {}).get("institutional_edition")
        institutional_edition = True if val else False
        return institutional_edition

    def is_autoship(self):
        """Checks if this item is an auto-ship item

        Returns:
          bool: True if the item is auto-ship False if it's not
        """
        is_autoship = re.search(r'[0-9]{1,3} day auto', self.get('name', ""), re.IGNORECASE)
        return True if is_autoship else False

    def is_missing_pers(self):
        """Checks if this item is personalized, that it has personalization values for all required fields,
        and that the number of personalization sets match the quantity

        Returns:
          bool: True if the item is missing any personalization, False if it's not
        """
        if (
            not self.get("product")
            or not isinstance(self.get("product"), Product)
            or not self.get("product").get("custom")
        ):
            return False

        # return true if number of personalization sets don't match quantity
        if not self.get("personalization") or len(self.get("personalization")) < self.get("quantity"):
            return True

        # return true if any of the prompts are required but don't have a value
        personalization = self.get("personalization")
        for i in range(0, self.get("quantity")):
            missing_required = next((d for d in personalization[i] if d.get("required") and not d.get("value")), None)
            if missing_required:
                return True

        return False

    def get_giftwrap_skuid(self):
        """If this item is a giftwrappable item, get the skuid of the giftwrap item

        Returns:
          str: The SKUID of the giftwrap/bag
        """

        gw_skuid = None
        product = self.get("product")
        if product:
          gw_skuid = product.get("giftwrap")
          # if this product is gift-wrappable and they are club members, use the club giftwrap sku
          if gw_skuid and current_app.config.get('STORE_CODE') == 'basbleu2' and g.cart.is_club_validated():
              gw_skuid = current_app.config.get('CLUB_GIFTWRAP')

        return gw_skuid

    def get_giftwrap_price(self):
        """If this item has giftwrap available (the giftwrap sku is in the product's giftwrap field), get the price

        Returns:
          float: Price of the giftwrap, or 0.00 if none
        """

        gw_price = 0.00
        giftwrap_skuid = self.get_giftwrap_skuid()
        if giftwrap_skuid:
          q = DB.fetch_one(
              "SELECT PRICE as gw_price FROM products WHERE SKUID = %(giftwrap_skuid)s LIMIT 1",
              {"giftwrap_skuid": giftwrap_skuid},
          )
          if q and q.get("gw_price"):
              return float(q.get("gw_price"))

        return gw_price

    def get_google_object(self):
        """Gets the cart item data as an object suitable for use in google analytics events

        Returns:
          dict: The cart item as a google object
        """
        variant_descs = [v["description"] for v in self.get("variant_data", [])]
        product = self.get("product")
        return {
            "name": sanitize(self.get("name")),
            "id": self.get("unoptioned_skuid"),
            "price": self.get("price"),
            "category": get_breadcrumb_string(product.get("breadcrumb", []), " > "),
            "variant": ", ".join(variant_descs),
            "quantity": self.get("quantity"),
            "dimension1": self.get("skuid"),
        }

    @staticmethod
    def get_base_skuid(skuid):
        """returns a skuid without variant code suffixes

        Args:
          skuid (str): The SKUID with variant suffixes

        Returns:
          str: The SKUID without the variant suffixes
        """

        base_skuid = None
        if "-" in skuid:
            base_skuid = skuid.split("-")[0]
        else:
            base_skuid = skuid

        return base_skuid.strip()

    @staticmethod
    def get_variant_data(item_dict=None):
        """
        For items with options (variants) that have been selected, load all associated variant data
        like variant type, descriptions and upcharges.  Uses 'variant_codes' key on item.

        Args:
          dict: The cart item as dictionary

        Returns:
          dict: A dictionary with the upcharge total and descriptions:
              {"upcharge": 0.00, "descriptions": []}
        """
        if not item_dict:
            return False

        variant_data = None
        # if it's an optioned item, see about upcharges
        variant_upcharges = 0.00
        if item_dict.get("variant_codes") and isinstance(item_dict["variant_codes"], list):
            # get the lists to check
            base_skuid = CartItem.get_base_skuid(item_dict["skuid"])
            variant_ref_list = get_variant_ref_list(base_skuid)

            # if length of the lists to check and the length of list of codes
            # corresponds, we're good
            if variant_ref_list and (len(variant_ref_list) == len(item_dict["variant_codes"])):
                variant_data = get_selected_variant_data(item_dict["variant_codes"], variant_ref_list)

        return variant_data

    @staticmethod
    def get_selected_image(skuid, product=None):
        """
        "queries" the product variant map to see if there is a specific image associated with the currently-selected variant

        Args:
          skuid (str): The full SKUID of the cart item
          product (Product): the product object associated with the cart item

        Returns:
          str: the image url of match is found, None if not
        """
        image = None
        if not skuid or not product or not isinstance(product.get("variant_map"), list):
            return image
        v = next(
            (p for p in product.get("variant_map") if p.get("fullskuid") == skuid and p.get("images")),
            None,
        )
        if v:
            image = v["images"].get("small") if v["images"].get("small") else v["images"].get("small")
        return image

    @staticmethod
    def get_prop65_message(skuid):
        """Gets specific CA PROP65 message for this item (if any).  Not an efficient query so it should only
        be called selectively (if selecting bill/ship is CA).

        Returns:
          str: The prop65 message
        """

        message = ""
        if not skuid:
            return message

        fullsku = skuid.replace("-", "")
        res = DB.fetch_one(
            """
              SELECT product_metadata.prop65, prop65_messages.message AS message
              FROM product_metadata, prop65_messages
              WHERE product_metadata.fullsku = %(fullsku)s
              AND product_metadata.prop65 = prop65_messages.code
            """,
            {"fullsku": fullsku},
        )
        if res and res.get("message"):
            message = res.get("message").replace(
                "www.P65warnings.ca.gov",
                '<a href="https://www.P65warnings.ca.gov" target="_new">www.P65warnings.ca.gov</a>',
            )
            message = (
                f'<img src="{current_app.config["IMAGE_BASE"]}/assets/images/prop65_warning.png" style="float: left;margin: 5px;"> '
                + message
            )
        return message

    @classmethod
    def from_dict(cls, item_dict=None):
        """Creates a CartItem object with the given item.

        Args:
          item_dict (dict): The item to be added.  Should have at least 'skuid'.  if not 'quantity' passed, defaults to 1.
          Example:
            {
              'skuid': 'HB0001',
              'quantity': 1,
              'variant_codes': ['SW', 'XL'],
              'personalization':     {
                "custom": "HB0001",
                "data": "DATA1",
                "id": 97404,
                "list": null,
                "maxlength": "13",
                "prompt": "Specify Up to 13 Characters.",
                "required": 1,
                "value": "O'Connor"
              }
            }

        Returns:
          CartItem: the instantiated CartItem oject (None if none)
        """

        if not item_dict or "skuid" not in item_dict:
            g.messages["errors"].append("No SKUID passed")
            return None

        # validate the skuid
        if not validate_skuid(item_dict["skuid"]):
            g.messages["errors"].append(f"Invalid SKUID")
            current_app.logger.error(f"Invalid SKUID attempted in Cartitem.from_dict: {item_dict['skuid']}")
            return None

        base_skuid = CartItem.get_base_skuid(item_dict["skuid"])

        # get the base product object
        product = Product.from_skuid(base_skuid, True)

        if not product:
            g.messages["errors"].append(f"Product does not exist")
            return None

        # check it's not NLA
        if product.get("nla") or (
            len(base_skuid) < len(item_dict["skuid"]) and not check_optioned_available(item_dict["skuid"])
        ):
          if f"Product {base_skuid} is not available" not in g.messages["errors"]:
            g.messages["errors"].append(f"Product {base_skuid} is not available.")
            return None

        # if product has variant sets, incoming item must have same number of codes
        if (
            product.get("variant_sets")
            and item_dict.get("variant_sets")
            and isinstance(item_dict["variant_sets"], list)
        ):
            if (
                not "variant_codes" in item_dict
                or not isinstance(item_dict["variant_codes"], list)
                or len(product.get("variant_sets")) != len(item_dict["variant_codes"])
            ):
                g.messages["errors"].append(
                    f"Product {sanitize(base_skuid)} has the incorrect number of options selected"
                )
                return None

        quant_tmp = item_dict.get("quantity", None)
        quantity = int(quant_tmp) if is_number(quant_tmp) and int(quant_tmp) > 0 else 1
        price = float(product.get("price")) if is_number(product.get("price")) else 0.00
        image = product.get("images").get("smlimg") if isinstance(product.get("images"), dict) else None
        cart_item = {
            "skuid": DB.esc(item_dict["skuid"]),
            "unoptioned_skuid": base_skuid,
            "quantity": quantity,
            "price": price,
            "name": product.get("name"),
            "origprice": float(product.get("origprice")) if is_number(product.get("origprice")) else 0.00,
            "ppd1_price": float(product.get("ppd1_price")) if is_number(product.get("ppd1_price")) else 0.00,
            "shipping": product.get("shipping"),
            "variant_codes": [],
            "variant_data": [],
            "variant_upcharges": [],
            "variant_origprice_upcharges": [],
            "personalization": item_dict["personalization"] if "personalization" in item_dict else [],
            "image": image_path(image) if image else current_app.config["DEFAULT_IMAGE"],
            "product": product,
            "availability": get_availability(item_dict["skuid"]),
            "is_tweaked": False,
        }

        # print("CARTITEM PERS")
        # print(cart_item["personalization"])
        # print(cart_item)

        # if it's an optioned item, get upcharges and assoc. variant info
        variant_data = CartItem.get_variant_data(item_dict)
        if variant_data:
            cart_item["variant_upcharges"] = variant_data["upcharge"]
            cart_item["variant_origprice_upcharges"] = variant_data.get("origprice_upcharge", 0.00)
            cart_item["variant_codes"] = item_dict["variant_codes"]
            cart_item["variant_data"] = variant_data["descriptions"]
            cart_item["skuid"] = base_skuid + "-" + "-".join(cart_item["variant_codes"])
            cart_item["price"] += variant_data["upcharge"]

            # update the product name so that it contains the selected options
            descs = [i.get("description") for i in variant_data["descriptions"]]
            cart_item["name"] += " - " + ", ".join(descs)

            # check if there's a specific image for this full skuid
            selected_image = CartItem.get_selected_image(cart_item["skuid"], product)
            if selected_image:
                cart_item["image"] = selected_image

        # apply any item-level tweaks (like discounts)
        cart_item = tweak_item(cart_item)

        # print("POST-TWEAK ITEM")
        # print(cart_item)

        return cls(cart_item)
