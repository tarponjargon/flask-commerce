from datetime import datetime
from flask import g, current_app
from copy import copy
from pprint import pprint
from flask_app.modules.cart.promos import apply_discount_by_type
from flask_app.modules.helpers import split_to_list
from flask_app.modules.preload import get_gdiscounts

def apply_gdiscount():
    """checks for any quantity discount or group discounts (containing this product).
    data is stored in gdiscounts table.  must obviously consider other items
    in cart

    NOTE: this mutates the cart item(s) directly using .set
    """

    gdiscounts = get_gdiscounts()
    for item in g.cart.get_items():
        # don't double-tweak
        if item.get("is_tweaked"):
            continue
        base_skuid = item.get_base_skuid(item.get("skuid"))
        if base_skuid in gdiscounts["index"]:
            # find the gdiscount(s) THERE CAN BE MORE THAN 1 - appends each to a list
            disc_list = []
            for i in gdiscounts["data"]:
                if base_skuid in i["skuids"]:
                    disc_list.append(i)

            if len(disc_list):
                # sort the list by quantity DESC
                disc_list_sorted = sorted(disc_list, key=lambda k: k["quantity"])
                gdiscount = disc_list_sorted[::-1]

                # loop thru gdiscount data (skus), and validate thresholds against cart
                # candidate item quantites
                for discount in gdiscount:
                    candidates = 0
                    for skuid in discount["skuids"]:
                        for i in g.cart.get_items():
                            candidates += i.get("quantity") if i.get_base_skuid(i.get("skuid")) == skuid else 0

                    # if quantity of item or group meets or exceeds discount threshold...go time
                    if candidates >= discount["quantity"]:
                        product_price = copy(item.get("price"))
                        price = apply_discount_by_type(product_price, discount)
                        item.set("price", price)
                        item.set("ppd1_price", product_price)
                        item.set("is_tweaked", True)
                        break

        # See if the item is in there as optioned
        if not item.get('is_tweaked') and item.get("skuid") in gdiscounts["index"]:
            # find the gdiscount(s) THERE CAN BE MORE THAN 1 - appends each to a list
            disc_list = []
            for i in gdiscounts["data"]:
                if item.get("skuid") in i["skuids"]:
                    disc_list.append(i)

            if len(disc_list):
                # sort the list by quantity DESC
                disc_list_sorted = sorted(disc_list, key=lambda k: k["quantity"])
                gdiscount = disc_list_sorted[::-1]

                # loop thru gdiscount data (skus), and validate thresholds against cart
                # candidate item quantites
                for discount in gdiscount:
                    candidates = 0
                    for skuid in discount["skuids"]:
                        for i in g.cart.get_items():
                            candidates += i.get("quantity") if i.get("skuid") == skuid else 0

                    # if quantity of item or group meets or exceeds discount threshold...go time
                    if candidates >= discount["quantity"]:
                        product_price = copy(item.get("price"))
                        price = apply_discount_by_type(product_price, discount)
                        item.set("price", price)
                        item.set("ppd1_price", product_price)
                        item.set("is_tweaked", True)
                        break