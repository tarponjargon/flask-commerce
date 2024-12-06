""" API routes for retrieving test data """

import re
from flask import Blueprint, request
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import is_number, sanitize

mod = Blueprint("test_api", __name__, url_prefix="/api/test")


@mod.route("/nonoptioned")
def do_get_nonoptioned():
    """Gets a non-optioned SKUID from products"""
    return DB.fetch_one(
        f"""
      SELECT SKUID AS skuid
      FROM products
      WHERE INVENTORY+0 != 1
      AND FEATUREABLE+0 = 1
      AND OPTIONS = ''
      AND CUSTOM = ''
      AND BACKORDER = ''
      AND LENGTH(SKUID) = 6
      AND DROP_SHIP = ''
      AND NO_PAYPAL = ''
      AND PRICE+0 > 0
      AND PRICE+0 < 100
      ORDER BY RAND()
      LIMIT 1
    """
    )


@mod.route("/testpreorder")
def do_get_preorder():
    """Gets a preorder item from products"""
    return DB.fetch_one(
        f"""
        SELECT SKUID as skuid
        FROM products
        WHERE (BACKORDER IS NOT NULL AND BACKORDER != '')
        AND INVENTORY+0 != 1
        AND PREORDER+0 = 1
        AND OPTIONS = ''
        AND CUSTOM = ''
        AND PRICE+0 > 0
        ORDER BY RAND()
        LIMIT 1
      """
    )


@mod.route("/testgroupid")
def do_get_groupid():
    """Gets an item that's part of a group of items from products"""
    return DB.fetch_one(
        f"""
          SELECT
            SKUID AS skuid,
            COUNT(*) AS GROUP_COUNT
          FROM products
          WHERE (GROUP_ID IS NOT NULL AND GROUP_ID != '')
          AND INVENTORY+0 != 1
          AND (CUSTOM IS NULL OR CUSTOM = '')
          AND LENGTH(SKUID) = 6
          GROUP BY GROUP_ID
          ORDER BY GROUP_COUNT DESC
          LIMIT 1
      """
    )


@mod.route("/testpreorderoptioned")
def do_get_preorderoptioned():
    """Gets an item that's both preorder and optioned from products"""
    return DB.fetch_one(
        f"""
          SELECT SKUID FROM products
          WHERE (OPTIONS IS NOT NULL AND OPTIONS != '' AND OPTIONS NOT LIKE '%%;%%')
          AND INVENTORY+0 = 1
          AND PREORDER+0 = 1
          AND CUSTOM = ''
          AND PRICE+0 > 0
          ORDER BY RAND() LIMIT 1
      """
    )


@mod.route("/testupcharge")
def do_get_testupcharge():
    """Gets an item that is optioned and has an upcharge"""
    return DB.fetch_one(
        f"""
          SELECT
            products.SKUID as skuid,
            options.pricechange as pricechange
          FROM products, options
          WHERE products.INVENTORY+0 != 1
          AND products.FEATUREABLE+0 = 1
          AND (products.OPTIONS IS NOT NULL AND products.OPTIONS != '' AND products.OPTIONS NOT LIKE '%%;%%')
          AND products.CUSTOM = ''
          AND products.BACKORDER = ''
          AND products.PRICE+0 > 0
          AND products.OPTIONS = options.sku
          AND options.pricechange > 0
          AND options.notstocked+0 != 1
          AND products.SKUID != 'GC9999'
          ORDER BY RAND()
          LIMIT 1
      """
    )


@mod.route("/testoptioned")
def do_get_testoptioned():
    """Gets a non-personalized item that has all options available/in stock"""

    for i in range(70):
        res = DB.fetch_one(
            f"""
          SELECT SKUID as TESTSKUID1
          FROM products
          WHERE INVENTORY+0 != 1
          AND FEATUREABLE+0 = 1
          AND OPTIONS LIKE '%%;%%'
          AND CUSTOM = ''
          AND LENGTH(SKUID) = 6
          AND BACKORDER = ''
          AND PRICE+0 > 0
          ORDER BY RAND()
          LIMIT 1
        """
        )
        if res and res.get("TESTSKUID1"):
            skuid = res.get("TESTSKUID1")
            q = DB.fetch_all(
                """
                  SELECT
                  `count`+0 AS TESTCOUNT,
                  `invcode` AS TESTINVCODE
                  FROM invdata
                  WHERE skuid LIKE %(skuid_wildcard)s
                """,
                {"skuid_wildcard": skuid + "%"},
            )
            if q and q.get("results"):
                instock = 0
                for result in q.get("results"):
                    if result.get("TESTCOUNT") > 0 and result.get("TESTINVCODE").startswith("R"):
                        instock = instock + 1

                if instock > 0 and instock == len(q.get("results")):
                    return {"skuid": skuid}

    return {}


@mod.route("/otest")
def do_get_otest():
    """takes in an order number and # of items and checks the db that it exists with that number if lineitems"""
    id = sanitize(request.values.get("otest_id"))
    lineitems = sanitize(request.values.get("otest_num"))

    if not id or not is_number(lineitems):
        return {"success": False}

    id = re.sub("[^0-9]", "", id)

    q = DB.fetch_all(
        """
          SELECT
            orders.order_id,
            orders_products.order_id
          FROM orders, orders_products
          WHERE orders.order_id = %(id)s
          AND orders.order_id = orders_products.order_id
        """,
        {"id": id},
    )

    if q and q.get("results") and len(q.get("results")) == int(lineitems):
        return {"success": True}

    return {"success": False}

@mod.route("/mytest")
def do_mytest():
  #raise ValueError("x should be a non-negative number")
  return {"success": True}
