""" Functions related to processing query parameters.

NOTE: This application automatically saves all qery parameters to the session"""

from pprint import pprint
import re
from copy import deepcopy
from urllib.parse import urlencode
from flask import current_app, g, request, session, redirect
from flask_app.modules.cart_item import CartItem
from flask_app.modules.http import get_request_values, session_get, get_session_id, get_cart_id
from flask_app.modules.helpers import is_number, quote_list, sanitize, validate_email, validate_skuid
from flask_app.modules.product.personalization import get_personalization_prompts
from flask_app.modules.extensions import DB
from flask_app.modules.preload import get_source_codes, get_discounts


def set_session_defaults():
    """Sets session variables to config defaults if not already set"""
    for key, value in current_app.config["SESSION_DEFAULTS"].items():
        if not session.get(key, None):
            session[key] = value
    if request.referrer and not session.get("my_referer"):
        session["my_referer"] = request.referrer


def save_params_to_session():
    """Saves query params and form data as keys in session to mimic Hazel's functionality"""

    values = get_request_values()

    for i in values.keys():
        key = i.lower()
        value = values.get(i)
        if not key or not isinstance(key, str):
            continue
        if not value or not isinstance(value, str):
            continue
        if len(key) > 255 or len(value) > 4096:
            current_app.logger.error(f"Key or value too long on request {request.path}: {key} (max 255) - {value} (max 4096)")
            continue
        if key not in current_app.config["FORBIDDEN_FIELDS"]:
            session[key] = value
            # print(key, session[key])


def check_promo_code():
    """Checks the request values for either coupon_code or source code.  If source_code is found it needs to be checked if there
    is an associated promotion.

    Returns:
      str: The coupon or source code that is tied to a promotion
    """

    # need to check both source and coupon code fields (against valid source codes list) as source codes can be added to either
    # force uppercase on source/coupon codes
    promo_code = None
    check_codes = []
    source_code = sanitize(session_get("source_code", "").upper())
    coupon_code = sanitize(session_get("coupon_code", "").upper())
    if source_code:
        check_codes.append(source_code)
    if coupon_code:
        check_codes.append(coupon_code)

    if not len(check_codes):
        return None

    employee_discounts = [i["code"] for i in current_app.config["EMPLOYEE_DISCOUNTS"]]
    cached_discounts = get_discounts()

    matched_source = next((x for x in check_codes if x in get_source_codes()), None)
    if matched_source:
        # if source code matched, make sure it gets set as the source code to the session (it may have been added as a coupon)
        session["source_code"] = matched_source

        # check if source code is tied to a promotion
        if matched_source in cached_discounts["index"]:

          # if this is not an employee discount, delete the coupon code to prevent customer from
          # also adding a coupon-driven promotion.  "stacking" is allowed for employees though
          if matched_source not in employee_discounts:

              current_app.logger.debug("SESSION: " + str(get_session_id()))
              current_app.logger.debug("CART: " + str(get_cart_id()))
              current_app.logger.debug("SOURCE CODE MATCHES PROMO: " + str(matched_source))
              session["coupon_code"] = None

          return matched_source

    # if a coupon code is entered
    if coupon_code:

        if not session_get('orig_coupon_code'):
          session['orig_coupon_code'] = coupon_code

        current_app.logger.debug("SESSION: " + str(get_session_id()))
        current_app.logger.debug("CART: " + str(get_cart_id()))

        if coupon_code in cached_discounts["index"]:
            # check against promotions index
            current_app.logger.debug("COUPON CODE MATCHED PROMO: " + str(coupon_code))
            return coupon_code
        elif coupon_code.upper() in employee_discounts:
            disc = next((x for x in current_app.config["EMPLOYEE_DISCOUNTS"] if x["code"] == coupon_code.upper()), {})
            g.messages["promo"] = f"Employee order. 40% Off. Delivered to {disc.get('location')}."
            session["source_code"] = coupon_code.upper()
            session["coupon_code"] = None
            current_app.logger.debug("EMPLOYEE COUPON CODE: " + str(coupon_code))
        else:
            # if not found, delete it and set an error message
            session["coupon_code"] = None
            g.messages["promo"] = f"{sanitize(coupon_code)} is not associated with a promotion"
            current_app.logger.debug("COUPON CODE DOES NOT MATCH PROMO: " + str(coupon_code))

    return None


def process_params():
    """Take specific actions (on any route) based on query params.  Inherited from hazel.

    OPTIONED_[SKUID]=[OPTIONS]&OPTIONED_QUANTITY_[SKUID]=[QUANTITY]: add an item with options
    BATCH_PRODUCT_[INDEX]=[SKUID]&BATCH_QUANTITY_[INDEX]=[QUANTITY]: add multiple items (skuid can be optioned) - 1-indexed
    PRODUCT_[SKUID]=[QUANTITY]: Add a single item (skuid can be optioned).  If the quantity is 0 the item is removed
    ACTION=ADD&ITEM=[SKUID]: Add a non-optioned item to the cart with a defaut qty of 1
    DATA1_[SKUID]_1=[PERSONALIZATION]&DATA1_[SKUID]_2=[PERSONALIZATION]&LAST_ADDED=[SKUID]: add personalization to an item

    Returns:
      None: this function is all side-effects
    """
    # create a querystring from args so it can be pattern-matched
    qs = urlencode(request.values.to_dict())

    if not qs:
        return None

    # /store?action=get_cart&cart=[id] was used on the old site to re-discover existing carts via a link (like an abandoned cart email)
    # I'm putting this here because this function processes request params on every request
    # this can be removed 6 mos after go-live
    if request.args.get("action") == "get_cart" and request.args.get("cart"):
        return redirect(current_app.config["STORE_URL"] + "/get_cart?" + request.query_string.decode("utf8"))

    # these are "if" instead of "elif" because any/all conditions can be true at the same time
    if re.search(r"[&]?PRODUCT_", qs, re.IGNORECASE):
        product_action()
    if "OPTIONED_" in qs.upper():
        optioned_add()
    if "BATCH_PRODUCT_" in qs.upper():
        batch_add()
    if re.search(r"[&]?ACTION=ADD", qs, re.IGNORECASE):
        item_add()
    if request.path == "/add" and re.search(r"[&]?ITEM=", qs, re.IGNORECASE):
        item_add()
    if re.search(r"[&]?DATA[0-9]{1,2}_", qs, re.IGNORECASE):
        add_personalization()
    if current_app.config.get("STORE_CODE") == 'basbleu2' and re.search(r"[&]?BILL_EMAIL=", qs, re.IGNORECASE):
        auth_club_by_email()
    return None

def auth_club_by_email():
    """ If the email is submitted and the customer is not club validated, try to use the email to validate """
    if not g.cart.is_club_validated() and not session_get("checked_club_email"):
      email = request.values.get("bill_email")
      if email and validate_email(email):
        session["checked_club_email"] = True
        custno = None
        q = """
          SELECT custno
          FROM bb_society WHERE email LIKE %(bill_email)s
          AND member_status = 'A'
          ORDER BY expiration DESC
          LIMIT 1
        """
        res = DB.fetch_one(q, {"bill_email": email})
        if res:
          custno = res.get("custno")
        if custno:
          session['BBSVALIDATED'] = "1"
          session['BBSMEMBER'] = res.get('custno')

def product_action():
    """Add item(s) to the cart that has the PRODUCT_[SKUID]=[QUANTITY] formatted params
    There can be multiple.

    Returns:
      list: The added CartItems (empty if none)
    """

    args = request.values
    key_prefix = "PRODUCT_"
    for k, v in args.items():
        if k.upper().startswith(key_prefix):
            skuid = k.upper().replace(key_prefix, "")
            quantity = 1
            try:
                quantity = int(v) if is_number(v) else 1
            except ValueError as e:
                quantity = 1

            if not skuid:
                g.messages["errors"].append("SKUID not passed in request")
                return None

            if not validate_skuid(skuid):
                g.messages["errors"].append(f"Invalid SKUID")
                current_app.logger.error(f"Invalid SKUID attempted in product_action: {skuid}")
                return None

            if quantity < 0:
                g.messages["errors"].append("Quantity cannot be negative - changed to 1")
                quantity = 1

            # if quantity is set to 0, remove the item from the cart
            if quantity == 0:
                return g.cart.remove_item(skuid)

            # if the sku string has variant codes, split them out into a list
            skuarr = skuid.split("-")
            if len(skuarr) > 1:
                base = skuarr.pop(0)
            item = CartItem.from_dict({"skuid": skuid, "quantity": quantity, "variant_codes": skuarr})
            g.cart.add_item(item)


def item_add():
    """Add 1 QTY of unoptioned item to the cart that has OPTIONED_[SKUID]=[OPTIONS]&OPTIONED_QUANTITY_[SKUID]=[QUANTITY] format

    Returns:
      CartItem: The added CartItem (empty if none)
    """

    args = request.values
    skuid = None
    quantity = 1
    for k, v in args.items():
        if k.upper() == "ITEM":
            skuid = v.upper()

    if not skuid:
        g.messages["errors"].append("SKUID not passed in request")
        return None

    if not validate_skuid(skuid):
        g.messages["errors"].append(f"Invalid SKUID")
        current_app.logger.error(f"Invalid SKUID attempted in item_add: {skuid}")
        return None

    item = CartItem.from_dict({"skuid": skuid, "quantity": quantity})
    if item:
        g.cart.add_item(item)


def optioned_add():
    """Add an optioned item to the cart that has the PRODUCT_[SKUID]=[QUANTITY] formatted params

    Returns:
      CartItem: The added CartItem (empty if none)
    """

    args = request.values
    skuid = None
    quantity = 1
    key_prefix = "OPTIONED_"
    optioned_str = ""
    for k, v in args.items():
        if k.upper().startswith(key_prefix):
            if k.upper().startswith("OPTIONED_QUANTITY_"):
                quantity = 1
                try:
                    quantity = int(v) if is_number(v) else 1
                except ValueError as e:
                    quantity = 1
            else:
                skuid = k.upper().replace(key_prefix, "") + "-" + v.upper()
                optioned_str = v.upper()

    if not skuid:
        g.messages["errors"].append("SKUID not passed in request")
        return None

    if not validate_skuid(skuid):
        g.messages["errors"].append(f"Invalid SKUID")
        current_app.logger.error(f"Invalid SKUID attempted in optioned_add: {skuid}")
        return None

    if quantity < 0:
        g.messages["errors"].append("Quantity cannot be negative - changed to 1")
        quantity = 1

    item = CartItem.from_dict({"skuid": skuid, "quantity": quantity, "variant_codes": optioned_str.split("-")})
    if item:
        g.cart.add_item(item)


def batch_add():
    """Add multiple optioned or unoptioned items using BATCH_PRODUCT_[INDEX]=[SKUID]&BATCH_QUANTITY_[INDEX]=[QUANTITY] format

    Returns:
      list: A list of the CartItem objects added, empty if none
    """

    # make a list of the indexes mentioned.  They may not always be sequential or in order
    args = request.values
    indexes = []
    key_prefix = "BATCH_PRODUCT_"
    key_prefix2 = "BATCH_QUANTITY_"
    for k, v in args.items():
        if k.upper().startswith(key_prefix):
            indexes.append(k.upper().replace(key_prefix, ""))

    if not len(indexes):
        g.messages["errors"].append("No items passed in request")
        return None

    for i in indexes:
        fullskuid = args.get(f"{key_prefix}{i}", args.get(f"{key_prefix.lower()}{i}"))
        q = args.get(f"{key_prefix2}{i}", args.get(f"{key_prefix2.lower()}{i}"))
        if not fullskuid or not q:
            return None
        quantity = int(q) if is_number(q) else 1
        if quantity < 0:
            quantity = 1
            g.messages["errors"].append(f"Quantity cannot be negative for item {i}, changed to quantity of 1")

        skuarr = fullskuid.split("-")
        skuid = skuarr.pop(0)

        if not skuid:
            g.messages["errors"].append(f"No skuid passed for item {i}")
        elif not validate_skuid(skuid):
            g.messages["errors"].append(f"Invalid SKUID")
            current_app.logger.error(f"Invalid SKUID attempted in batch_add: {skuid}")
        else:
            item = CartItem.from_dict({"skuid": skuid, "quantity": quantity, "variant_codes": skuarr})
            if item:
                g.cart.add_item(item)


def add_personalization():
    """Add personalization to CartItem from params with format: DATA1_[SKUID]_1=[PERSONALIZATION]&DATA1_[SKUID]_2=[PERSONALIZATION]

    Does require some regex heavy lifting
    """

    args = request.values
    raw_pers = {}
    key_prefix = "DATA"
    has_missing_required = False

    # parse personalization query string into a dict: {skuid.[quantity each].[prompt values]}.  EXAMPLE:
    #      {
    #       'HX7492-WP': [
    #            {'line': 'DATA1', 'qtyref': 1, 'value': 'rory'},
    #            {'line': 'DATA2', 'qtyref': 1, 'value': 'hello rory'},
    #            {'line': 'DATA3', 'qtyref': 1, 'value': 'rory rory 2'},
    #            {'line': 'DATA1', 'qtyref': 2, 'value': 'dina'},
    #            {'line': 'DATA2', 'qtyref': 2, 'value': 'hello dina'},
    #            {'line': 'DATA3', 'qtyref': 2, 'value': 'hello dina 2'}
    #          ]
    #        }
    for k, v in args.items():
        if k.upper().startswith(key_prefix):
            res = re.search(r"(DATA[0-9]{1,2})_([A-Za-z0-9\-]{4,})_([0-9]{1,2})", k, re.IGNORECASE)
            if res and res.groups and len(res.groups()) == 3:
                skuid = res.group(2).upper()
                if not skuid in raw_pers:
                    raw_pers[skuid] = []
                raw_pers[skuid].append({"line": res.group(1).upper(), "qtyref": int(res.group(3)), "value": v if isinstance(v, str) and len(v) < 4096 else ""})

    # pprint(raw_pers)

    # loop thru keys of the raw_pers dict and load associated CartItem, then get its personalization model
    for skuid in raw_pers.keys():
        item = g.cart.get_item_by_skuid(skuid)
        if not item:
            continue
        existing_pers = item.get("personalization", [])

        # if product['custom_special'] is truthy it means that the personalization key (when selecting from personalization_loop)
        # should be the fully-optioned skuid rather than the default product['custom'] value
        product = item.get("product", {})
        pers_key = item.get("skuid") if product.get("custom_special") else product.get("custom")
        model = get_personalization_prompts(pers_key)

        # create a personalization list (a list of lists).  The outer list is qty eaches,
        # the inner list is a list if prompts for the item   EXAMPLE:
        # [
        #   [
        #     {
        #       'custom': 'HX6612',
        #       'data': 'DATA1',
        #       'id': 97227,
        #       'list': None,
        #       'maxlength': '12',
        #       'prompt': 'Name up to 12 characters',
        #       'required': 1,
        #       'value': ''
        #     },
        #     { ... PROMPT 2 ...}
        #   ],
        #   [
        #     {
        #       'custom': 'HX6612',
        #       'data': 'DATA1',
        #       'id': 97227,
        #       'list': None,
        #       'maxlength': '12',
        #       'prompt': 'Name up to 12 characters',
        #       'required': 1,
        #       'value': ''
        #     },
        #     { ... PROMPT 2 ...}
        #   ]
        # ]
        personalization = []

        # create a list of personalization sets for each quantity.  include sets that are already there
        # as this function will replace the entire list
        for i in range(item.get("quantity")):
            if len(existing_pers) > i:
                personalization.append(deepcopy(existing_pers[i]))
            else:
                personalization.append(deepcopy(model))

        # populate the personalization list with values from pers[skuid] (joined on 'data' value like DATA1 == DATA1)
        for prompt in raw_pers[skuid]:
            qtyindex = prompt["qtyref"] - 1  # the index of the personalization list we're about to update
            try:
                i = next((i for (i, d) in enumerate(personalization[qtyindex]) if d.get("data") == prompt["line"]), -1)
                if i > -1:
                    if personalization[qtyindex][i]["required"] and not prompt["value"]:
                        has_missing_required = True
                    else:
                        personalization[qtyindex][i]["value"] = prompt["value"]
            except IndexError:
                current_app.logger.error(f"Index {qtyindex} doesn't exist in personalization:")
                current_app.logger.error(personalization)
                current_app.logger.error(f"request URL")
                current_app.logger.error(request.url)

        if has_missing_required:
            g.messages["errors"].append(
                f"Please enter all the personalization for {sanitize(item.get('name'))} or the word 'none'"
            )

        item.set("personalization", personalization)
