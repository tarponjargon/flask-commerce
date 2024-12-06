""" Quickorder route Blueprint """


from itertools import product
from flask import Blueprint, render_template, request, g, current_app
from flask_app.modules.cart_item import CartItem
from flask_app.modules.product import Product
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import quote_list, dedupe, sanitize

mod = Blueprint("quickorder_view", __name__)


@mod.route("/quickorder")
def quickorder_view():
    """Renders view for the quickorder/tax calculation app"""
    return render_template("quickorder.html.j2")


@mod.route("/buildorder")
def orderbuilder_view():
    """Renders HTML fragments for the /quickorder app"""

    # skus come in as request params, space delimited.  convert to array
    to_add = [sanitize(i.upper()) for i in request.args.get("ADDSKUIDS", "").split()]
    validskus = []
    optioned = []
    unoptioned = []
    overlimit = []

    if to_add and len(to_add):
        q = DB.fetch_all(
            "SELECT SKUID,OPTIONS FROM products WHERE SKUID IN %(to_add)s AND INVENTORY != 1",
            {"to_add": tuple(to_add)},
        )
        for res in q["results"]:
            validskus.append(res.get("SKUID"))

            # if the product requires options, load the product objects in a list
            if res.get("OPTIONS"):
                optioned.append(Product.from_skuid(res.get("SKUID")))

            # if the item doesn't require options add it directly to the cart
            else:
                unoptioned.append(res.get("SKUID"))
                cart_item = CartItem.from_dict({"skuid": res.get("SKUID")})
                # if the item is already in the cart, increment the quantity of the incoming item
                existing_item = g.cart.get_item_by_skuid(res.get("SKUID"))
                if existing_item:
                    cart_item.set("quantity", existing_item.get("quantity") + 1)
                if (len(g.cart.get_items()) < current_app.config['LINEITEM_LIMIT']):
                  g.cart.add_item(cart_item)
                else:
                  overlimit.append(res.get("SKUID"))

    invalidskus = [x for x in to_add if x not in validskus]
    return render_template("partials/buildorder.html.j2", invalidskus=dedupe(invalidskus), optioned=optioned, validskus=validskus, overlimit=dedupe(overlimit))
