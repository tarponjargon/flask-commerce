""" Functions related to a customer's wishlist """

import hashlib
from flask import current_app, session
from flask_app.modules.product import Product
from flask_app.modules.helpers import (
    get_random_string,
    is_number,
    jpg_extension,
    sanitize,
    split_to_list,
)
from flask_app.modules.extensions import DB


def get_hwlid(customer_id):
    """Gets existing wishlist id by customer_id.

    each wishlist has a unique ID called 'hwlid' that is written to each wishlist item record.
    It is just an an assigned random MD5 hash

    Args:
      customer_id (int): The customer ID

    Returns:
      str: a 32-char MD5 hash
    """

    q = DB.fetch_one(
        "SELECT hwlid FROM wishlist WHERE customer_id = %(customer_id)s GROUP BY hwlid", {"customer_id": customer_id}
    )
    return q.get("hwlid") if q and q.get("hwlid") else ""


def get_wishlist(hwlid):
    """Get customer wishlist items by customer_id OR hwlid (the wishlist id)

    Args:
      hwlid (str): The 32-char wishlist ID

    Returns:
      dict: A dictionary, the keys being hwlid (a 1-way hash of the customer id), and a list of item dictionaries
    """

    items = []
    if not hwlid:
      return {"hwlid": hwlid, "items": items}

    res = DB.fetch_all(
        """
          SELECT
            wl_skuid,
            hwlid,
            quantity,
            DATE_FORMAT(timestamp, '%%Y%%m%%d') AS date_added
          FROM wishlist
          WHERE hwlid = %(hwlid)s
        """,
        {"hwlid": hwlid},
    )["results"]

    for wl_item in res:
        hwlid = wl_item.get("hwlid")
        product = Product.from_skuid(wl_item.get("wl_skuid"))
        if product and not product.get("nla"):
            items.append(
                {
                    "quantity": wl_item.get("quantity"),
                    "dateAdded": int(wl_item.get("date_added")),
                    "skuid": product.get("skuid"),
                    "itemName": product.get("name"),
                    "price": float(product.get("price")),
                    "totalPrice": float(product.get("price")) * wl_item.get("quantity"),
                    "hasOptions": True if product.get("options") else False,
                    "productUrl": product.get("url"),
                    "thumbPath": "/graphics/products/small/" + jpg_extension(product.get("smlimg", "")),
                    "nla": False,
                    "productExists": product.get("skuid"),
                    "isOrderProduct": 1,
                    "maxq": product.get("maxq") if product.get("maxq") else current_app.config["DEFAULT_MAXQ"],
                }
            )

    return {"hwlid": hwlid, "items": items}


def upsert_wishlist_item(skuid, hwlid, qty=1):
    """
    Upsert an item on User's wishlist.

    Args:
      skuid (str): The SKU if the item to update/insert
      hwlid (str): THe 32-char wishlist ID.  If empty, one is created
      qty (int): The quanity of the item to add

    Returns:
      dict: A success or fail payload
    """
    product = Product.from_skuid(skuid)
    if not product:
        return {"success": False, "error": True, "errors": ["Product not found"]}

    if not qty or not is_number(qty):
        qty = 1
    success = 0

    has_wishlist = DB.fetch_one("SELECT COUNT(*) as has_wl FROM wishlist WHERE hwlid = %(hwlid)s", {"hwlid": hwlid})[
        "has_wl"
    ]

    if has_wishlist:
        has_product = DB.fetch_one(
            "SELECT COUNT(*) as has_product FROM wishlist WHERE wl_skuid = %(skuid)s AND hwlid = %(hwlid)s",
            {"skuid": skuid, "hwlid": hwlid},
        )["has_product"]
        if has_product:
            success = DB.update_query(
                "UPDATE wishlist SET quantity = quantity+%(qty)s, timestamp = NOW() WHERE wl_skuid = %(skuid)s AND hwlid = %(hwlid)s",
                {"qty": qty, "skuid": skuid, "hwlid": hwlid},
            )
        else:
            success = DB.insert_query(
                """
                  INSERT INTO wishlist SET
                  quantity = %(qty)s,
                  hwlid = %(hwlid)s,
                  customer_id = %(customer_id)s,
                  wl_skuid = %(skuid)s,
                  timestamp = NOW()
                """,
                {"qty": qty, "customer_id": session.get("customer_id"), "skuid": skuid, "hwlid": hwlid},
            )
    else:
        hwlid = hashlib.md5(get_random_string().encode("utf-8")).hexdigest()
        success = DB.insert_query(
            """
                INSERT INTO wishlist SET
                quantity = %(qty)s,
                hwlid = %(hwlid)s,
                customer_id = %(customer_id)s,
                wl_skuid = %(skuid)s,
                timestamp = NOW()
              """,
            {"qty": qty, "customer_id": session.get("customer_id"), "skuid": skuid, "hwlid": hwlid},
        )

    if not success:
        return {"success": False, "error": True, "errors": ["Problem updating wishlist item."]}

    return {"success": True, "error": False}


def delete_wishlist_item(skuids, hwlid):
    """
    Delete an item from the User's wishlist.  Not part of the User object because other people
    can remove items from a User's wishlist (by purchasing them for the user)

    Args:
      skuid (str): A semicolon delimited list of skuids
      hwlid (str): A random, assigned MD5 hash
    """

    sql = "DELETE FROM wishlist WHERE wl_skuid IN %(skuid_list)s AND hwlid = %(hwlid)s"
    success = DB.delete_query(sql, {"skuid_list": tuple(split_to_list(skuids)), "hwlid": hwlid})
    if not success:
        return {"success": False, "error": True, "errors": ["Problem removing item."]}

    return {"success": True, "error": False}
