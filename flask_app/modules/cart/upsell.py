""" Functions related to cart upsells """

from flask import g
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import is_number, quote_list
from flask_app.modules.http import session_get
from flask_app.modules.product import Product


def get_upsell_id():
    """Get an upsell item to present to the customer (if eligible)

    Returns:
      int: The id of the upsell product (in 'cart_upsells') to show
    """

    upsell_id = None

    # if the cart has any "slapper" items, do not present any upsells
    if g.cart.has_slapper():
        return None

    # if they have already seen the upsell, don't keep showing it
    if session_get("US_REFUSED") or session_get("SO_ACCEPT"):
        return None

    # create a list of base SKUs already in the cart and use a NOT IN sql clause to be
    # sure that they don't get offered a lower price on an item they are already purchasing
    skuids_clause = ""
    if not g.cart.is_empty():
        skuids_clause = "AND cart_upsells.skuid NOT IN %(cart_skuids)s"

    upsell = DB.fetch_one(
        f"""
          SELECT
            cart_upsells.id AS cart_upsell_id,
            cart_upsells.skuid AS cart_upsell_skuid
          FROM cart_upsells, products
          WHERE cart_upsells.start_date < NOW()
          AND cart_upsells.end_date > NOW()
          AND cart_upsells.skuid = products.SKUID
          AND products.INVENTORY != 1
          {skuids_clause}
          ORDER BY cart_upsells.priority ASC, cart_upsells.id DESC
          LIMIT 1
        """,
        {"cart_skuids": tuple(g.cart.get_base_skuids())},
    )
    if upsell:
        upsell_id = upsell["cart_upsell_id"]

    return upsell_id


def get_upsell_by_id(id):
    """Get an upsell product by it's id ('cart_upsells' table)

    Args:
      id (int): The id of the upsell to get

    Returns:
      dict: A dictionary containing the upsell product info
    """

    if not is_number(id):
        return None

    # I do tend to pack alot of logic into the SQL...
    # - if product_title not specified in cart_upsells, use default products.NAME
    # - if custom image not specified, use default products.SMLIMG
    # - if the products.PRICE is less than cart_upsells.price, make ad price the products.PRICE
    #     (this can happen with clearance items who's price is always being reduced)
    # - if products.PRICE is less than cart_upsells.breakprice, delete breakprice (same reason as above)
    # - if products's origprice > cart_upsells.origprice make origprice the product's
    upsell = DB.fetch_one(
        """
          SELECT
            cart_upsells.id,
            cart_upsells.skuid,
            cart_upsells.headline,
            cart_upsells.subhead,
            IF(cart_upsells.product_title IS NULL or cart_upsells.product_title = '',
              products.NAME,
              cart_upsells.product_title
            ) as product_title,
            cart_upsells.product_copy,
            cart_upsells.price_prefix,
            cart_upsells.start_date,
            cart_upsells.end_date,
            IF(products.PRICE+0 < cart_upsells.break_price+0,
              NULL,
              cart_upsells.break_price+0
            ) as break_price,
            IF(products.PRICE+0 < cart_upsells.break_price+0,
              NULL,
              cart_upsells.break_qty
            ) as break_qty,
            IF(products.PRICE+0 < cart_upsells.price+0,
              products.PRICE+0,
              cart_upsells.price+0
            ) as price,
            IF(products.ORIGPRICE+0 > cart_upsells.origprice+0,
              products.ORIGPRICE+0,
              cart_upsells.origprice+0
            ) as origprice,
            IF(cart_upsells.image IS NULL or cart_upsells.image = '0' or cart_upsells.image = '',
              CONCAT('/graphics/products/small/', products.SMLIMG, '.jpg'),
              CONCAT('/graphics/products/small/', cart_upsells.image, '.jpg')
            ) as image
          FROM cart_upsells, products
          WHERE cart_upsells.id = %(id)s
          AND cart_upsells.skuid = products.SKUID
        """,
        {"id": id},
    )

    # load the product base data into the upsell object
    if upsell:
        upsell["product"] = Product.from_skuid(upsell["skuid"])

    return upsell
