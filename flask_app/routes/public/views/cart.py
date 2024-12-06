""" View routes related to the cart """

import re
from flask import Blueprint, current_app, redirect, request, g, render_template
from flask_app.modules.cart.upsell import get_upsell_id
from flask_app.modules.helpers import is_number

from flask_app.modules.http import get_request_values

mod = Blueprint("cart_view", __name__)


@mod.route("/cart", methods=["GET", "POST"])
@mod.route("/add", methods=["GET", "POST"])
def do_cart_view():
    # template=ajax_cartadd.html told hazel to return json instead of html
    if request.args.get("template") == "ajax_cartadd.html":
        return {"cart": g.cart.to_dict(False)}

    """Returns the cart view"""
    if request.args.get("template") == "cartadd.html":
        return render_template("partials/cartadd.html.j2", cart=g.cart, last_added=g.cart.get_last_added())

    if g.cart.is_empty():
        return render_template("cartempty.html.j2")

    missing_variant_item = g.cart.has_missing_variants()
    if missing_variant_item:
        return render_template(
            "missing_variants.html.j2",
            product=missing_variant_item.get("product"),
            removeskuid=missing_variant_item.get("skuid"),
        )

    missing_pers_items = g.cart.has_missing_pers()
    if missing_pers_items:
        return render_template("missing_personalization.html.j2", items=missing_pers_items)

    return render_template("cart.html.j2", cart=g.cart, upsell_id=get_upsell_id())


@mod.route("/quick-add")
def do_cart_add_view():
    """Adds item(s) to the cart and returns personalization HTML fragment (if needed) or "popcart" HTML fragment"""
    last_added = g.cart.get_last_added()
    last_added_skuid = last_added.get("skuid") if last_added else None
    last_added_param = request.args.get("last_added")

    # if add was unsuccessful
    if len(g.messages['errors']):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          return {
            'error': True,
            'success': False,
            'errors': g.messages['errors']
          }
        else:
          return render_template("partials/cart_add_error.html.j2"), 404

    if last_added_param and last_added_param != last_added_skuid:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          return {
            'error': True,
            'success': False,
            'errors': ["Product not found"]
          }
        else:
          return render_template("partials/not_found.html.j2"), 404

    # template=ajax_cartadd.html told hazel to return json instead of html
    if request.args.get("template") == "ajax_cartadd.html":
        return {"cart": g.cart.to_dict(False)}

    last_added = g.cart.get_last_added()

    # make sure personalization has been collected
    if last_added.is_missing_pers():
        return render_template("partials/personalization.html.j2", last_added=last_added)
    else:
        return render_template("partials/cartadd.html.j2", cart=g.cart, last_added=last_added)


@mod.route("/selectoptions")
def do_select_options():
    """Convert query string from this format:
    ADDSKUIDS=HY7091%20HAF971%20HAV971&HY7091_QTY=2&HAF971_QTY=1&HAV971_QTY=1

    To this format:

    BATCH_PRODUCT_1=HY7091&BATCH_QUANTITY_1=1&BATCH_PRODUCT_2=HAF971&BATCH_QUANTITY_2=2&BATCH_PRODUCT_3=HAV971&BATCH_QUANTITY_3=1

    And redirect so that the items will be added to the cart and customer will be prompted to select any options
    """

    values = get_request_values()
    params = []
    sku_counter = 0
    for k, v in values.items():
        res = re.search(r"([A-Z0-9]{4,9})_QTY", k, re.IGNORECASE)
        if res and res.groups and len(res.groups()):
            sku_counter = sku_counter + 1
            skuid = res.group(1).upper()
            quantity = str(v) if is_number(v) else 1
            params.append(f"BATCH_PRODUCT_{sku_counter}={skuid}&BATCH_QUANTITY_{sku_counter}={quantity}")

    return redirect(current_app.config["STORE_URL"] + "/cart?" + "&".join(params))


@mod.route("/minicart")
def do_minicart_view():
    """Returns the mini-cart HTML fragment"""
    return render_template("partials/minicart.html.j2", cart=g.cart)


@mod.route("/editpersonalization")
def do_edit_pers():
    """Returns personalization HTML fragment"""
    last_added = g.cart.get_item_by_skuid(request.args.get("last_added"))
    returnpage = request.args.get("returnpage")
    return render_template("partials/personalization.html.j2", last_added=last_added, returnpage=returnpage)
