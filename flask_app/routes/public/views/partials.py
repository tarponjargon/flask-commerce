""" Partials route Blueprint

Flask Blueprint for rendering partial HTML into the DOM via Fetch
"""

from flask import Blueprint, render_template, request, g
from flask_app.modules.cart.upsell import get_upsell_by_id
from flask_app.modules.extensions import DB
from flask_app.modules.extensions import cache
from flask_app.modules.helpers import is_number
from flask_app.modules.http import page_not_found

mod = Blueprint("partials_view", __name__)


def get_bestsellers(category_code, features=4):
    """Generates a list of bestselling products for a given category

    Args:
      category_code (str): the category code
      features: (int): number of products to return (default: 4)


    Returns:
      list: A list of dictionaries (products)
    """

    from flask_app.modules.product import Product

    products = []
    sql = """
            SELECT
              bestsellers_by_category.skuid AS skuid,
              bestsellers_by_category.count,
              CONCAT("/", products.skuid, ".html") AS url,
              products.*
            FROM bestsellers_by_category,products
            WHERE bestsellers_by_category.skuid=products.SKUID
            AND bestsellers_by_category.category_code = %(category_code)s
            AND products.FEATUREABLE = '1'
            ORDER BY RAND()
            LIMIT %(features)s
          """
    params = {"category_code": category_code, "limit": features}
    results = DB.fetch_all(sql, params)["results"]
    for res in results:
        product = Product.from_skuid(res.get("skuid"), False)
        products.append(product.get_product())

    return products


@mod.route("/partials/category/<string:category>")
def partials_view(category):
    """Renders text/html for category partial

    Args:
      category (str): the category to find bestsellers for

    Returns:
      str: Partial template rendered as text/html
    """

    products = get_bestsellers(category)
    return render_template("partials/category.html.j2", products=products)


@mod.route("/email_capture")
def do_email_capture():
    """Renders the e-mail collection HTML fragment (usually shown in a modal)"""
    return render_template("partials/email_capture.html.j2")


@mod.route("/email_capture_drawer")
def do_email_capture_drawer():
    """Renders the e-mail collection HTML fragment (in a slide-up drawer)"""
    return render_template("partials/email_capture_drawer.html.j2")


@mod.route("/cart-upsell")
def do_cart_upsell():
    """Returns cart_upsell HTML fragment"""
    id = request.values.get("cart_upsell_id")
    if not id or not is_number(id):
        return page_not_found(None)

    upsell = get_upsell_by_id(id)
    if not upsell:
        return page_not_found(None)

    return render_template("partials/cart_upsell.html.j2", upsell=upsell)


@mod.route("/free-gift")
def do_free_gift():
    """Returns free gift HTML fragment"""
    if g and 'prompt_free_gift' in g and g.prompt_free_gift:
      return render_template("partials/free_gift.html.j2")
    else:
      return page_not_found(None)
