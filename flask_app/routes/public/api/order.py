""" API routes related to orders"""

import re
import json
from flask import Blueprint, current_app, request
from flask_app.modules.extensions import DB
from flask_app.modules.http import session_get
from flask_app.modules.helpers import image_path, is_float, is_int
from flask_app.modules.user.orders import get_tracking_link
from json.decoder import JSONDecodeError

mod = Blueprint("order_api", __name__, url_prefix="/api")


def get_lastname_by_orderid(orderid):
    """Gets lastname for customer by order id

    Customer must be logged in.

    Args:
      orderid (str): The order ID

    Returns:
      str: Customer last name or empty string
    """
    customer_id = session_get("customer_id")
    if not customer_id or not orderid or not re.match("^[0-9]{6,9}$", orderid):
        return ""

    if session_get("bill_lname"):
        return session_get("bill_lname", "")

    query = """
              SELECT bill_lname
              FROM orders
              WHERE order_id = %(orderid)s
              AND customer_id = %(customer_id)s
            """
    r = DB.fetch_one(query, {"orderid": orderid, "customer_id": customer_id})

    return r.get("bill_lname", "")


def get_zip_by_orderid(orderid):
    """Gets zip code for customer by order id

    Customer must be logged in.

    Returns:
      str: zip code or empty string
    """
    customer_id = session_get("customer_id")
    if not customer_id or not orderid or not re.match("^[0-9]{6,9}$", orderid):
        return ""

    if session_get("bill_postal_code"):
        return session_get("bill_postal_code", "")

    query = """
              SELECT bill_postal_code
              FROM orders
              WHERE order_id = %(orderid)s
              AND customer_id = %(customer_id)s
            """
    r = DB.fetch_one(query, {"orderid": orderid, "customer_id": customer_id})

    return r.get("bill_postal_code", "")


@mod.route("/orderstatus")
def do_orderstatus():
    """Returns customer's order status as JSON"""
    orderid = request.args.get("orderid", "")
    orderid = re.sub("[^0-9]", "", orderid)
    bill_lname = request.args.get("bill_lname", get_lastname_by_orderid(orderid))
    bill_postal_code = request.args.get("bill_postal_code", get_zip_by_orderid(orderid))
    bill_postal_code = re.sub(r"[^a-zA-Z0-9]", "", bill_postal_code)

    order = {"items": []}
    query_type = None
    query = None
    order_fields = [
        "orderId",
        "billingFirstName",
        "billingLastName",
        "billingAddress1",
        "billingAddress2",
        "billingCity",
        "billingState",
        "billingPostalCode",
        "billingCountry",
        "billingEmail",
        "shippingFirstName",
        "shippingLastName",
        "shippingAddress1",
        "shippingAddress2",
        "shippingCity",
        "shippingState",
        "shippingPostalCode",
        "shippingCountry",
        "giftWrap",
        "giftMessage",
        "comments",
        "notes",
        "paymentMethod",
        "shipMethod",
        "couponCode",
        "sourceCode",
        "totalDiscount",
        "totalSubtotal",
        "totalShipping",
        "totalTax",
        "totalCredit",
        "totalOrder",
        "date",
        "orderDate",
    ]
    item_fields = [
        "itemStatus",
        "isOrderProduct",
        "quantity",
        "skuid",
        "baseSkuid",
        "itemName",
        "optionedNotes",
        "optionedSuffix",
        "personalization",
        "price",
        "totalPrice",
        "shipMethodCode",
        "shipMethodName",
        "shipDate",
        "entryDate",
        "trackingNumber",
        "smartLabel",
        "itemThumb",
        "nla",
        "productExists",
        "isGiftwrap",
        "hasOptions",
        "maxq",
    ]

    if not orderid or not re.match("^[0-9]{6,9}$", orderid):
        return {"success": False, "error": True, "errors": ["Order IDs contain 6-9 numbers"]}

    if not bill_lname or not re.match("[A-Za-z0-9]{1,}", bill_lname):
        return {
            "success": False,
            "error": True,
            "errors": ["Please enter a billing last name or billing company name"],
        }

    if not bill_postal_code or not re.match("^[A-Za-z0-9]{5,12}$", bill_postal_code):
        return {"success": False, "error": True, "errors": ["Check your zip/postal code"]}

    # capture canada postal code
    if re.match("^[A-Za-z0-9]{6,}$", bill_postal_code):
        bill_postal_code = bill_postal_code[0:6]

    # if US zip, just get first 5
    if re.match("^[0-9]{5,}$", bill_postal_code):
        bill_postal_code = bill_postal_code[0:5]

    # check if order is in status table
    status_q = """
                  SELECT id FROM status
                  WHERE status.ordno RLIKE %(ordno_rlike)s
                  AND status.bill_zip RLIKE %(zip_rlike)s
                  LIMIT 1
                """
    status_check = DB.fetch_one(
        status_q, {"ordno_rlike": "^[A-Z][A-Z]?" + orderid + "$", "zip_rlike": "^" + bill_postal_code}
    )
    if status_check and status_check.get("id"):
        query_type = "status"

    if not query_type:
        orders_q = """
                    SELECT id FROM orders
                    WHERE order_id = %(orderid)s
                    AND bill_postal_code RLIKE %(zip_rlike)s
                  """
        orders_check = DB.fetch_one(orders_q, {"orderid": orderid, "zip_rlike": "^" + bill_postal_code})
        if orders_check and orders_check.get("id"):
            query_type = "order"

    if not query_type:
        return {
            "success": False,
            "error": True,
            "errors": ["No order found.  Please check your order ID. Contact us if you think this is in error."],
        }

    params = {"orderid": orderid, "zip_rlike": "^" + bill_postal_code}
    if query_type == "status":
        params["orderid_rlike"] = "^[A-Z][A-Z]?" + orderid + "$"
        query = """
        SELECT
          SUBSTRING(status.ordno, 2, 9) AS orderId,
          IF(orders.bill_fname IS NULL or orders.bill_fname = '', status.bill_fname, orders.bill_fname) as billingFirstName,
          IF(orders.bill_lname IS NULL or orders.bill_lname = '', status.bill_lname, orders.bill_lname) as billingLastName,
          IF(orders.bill_street IS NULL or orders.bill_street = '', NULL, orders.bill_street) as billingAddress1,
          IF(orders.bill_street2 IS NULL or orders.bill_street2 = '', NULL, orders.bill_street2) as billingAddress2,
          IF(orders.bill_city IS NULL or orders.bill_city = '', NULL, orders.bill_city) as billingCity,
          IF(orders.bill_state IS NULL or orders.bill_state = '', NULL, orders.bill_state) as billingState,
          IF(orders.bill_postal_code IS NULL or orders.bill_postal_code = '', status.bill_zip, orders.bill_postal_code) as billingPostalCode,
          IF(orders.bill_country IS NULL or orders.bill_country = '', NULL, orders.bill_country) as billingCountry,
          IF(orders.bill_email IS NULL or orders.bill_email = '', LOWER(status.email), LOWER(orders.bill_email)) as billingEmail,
          SUBSTRING_INDEX(status.name, ' ', 1) as shippingFirstName,
          TRIM(REPLACE(status.name, SUBSTRING_INDEX(status.name, ' ', 1), '')) as shippingLastName,
          status.address1 AS shippingAddress1,
          NULL AS shippingAddress2,
          status.city AS shippingCity,
          status.state AS shippingState,
          status.zip AS shippingPostalCode,
          NULL AS shippingCountry,
          IF(orders.gift_wrap IS NULL or orders.gift_wrap = '', NULL, orders.gift_wrap) as giftWrap,
          IF(orders.gift_message IS NULL or orders.gift_message = '', NULL, orders.gift_message) as giftMessage,
          IF(orders.comments IS NULL or orders.comments = '', NULL, orders.comments) as comments,
          IF(orders.notes IS NULL or orders.notes = '', NULL, orders.notes) as notes,
          IF(orders.payment_method IS NULL or orders.payment_method = '', NULL, orders.payment_method) as paymentMethod,
          IF(orders.ship_method IS NULL or orders.ship_method = '', NULL, orders.ship_method) as shipMethod,
          IF(orders.coupon_code IS NULL or orders.coupon_code = '', NULL, orders.coupon_code) as couponCode,
          IF(orders.source_code IS NULL or orders.source_code = '', NULL, orders.source_code) as sourceCode,
          IF(orders.total_discount IS NULL or orders.total_discount = '', '0.00', orders.total_discount) as totalDiscount,
          IF(orders.total_subtotal IS NULL or orders.total_subtotal = '', '0.00', orders.total_subtotal) as totalSubtotal,
          IF(orders.total_shipping IS NULL or orders.total_shipping = '', '0.00', orders.total_shipping) as totalShipping,
          IF(orders.total_tax IS NULL or orders.total_tax = '', '0.00', orders.total_tax) as totalTax,
          IF(orders.total_credit IS NULL or orders.total_credit = '', '0.00', orders.total_credit) as totalCredit,
          IF(orders.total_order IS NULL or orders.total_order = '', '0.00', orders.total_order) as totalOrder,
          IF(orders.date IS NULL, NULL, orders.date) as 'date',
          IF(orders.date IS NULL, NULL, DATE_FORMAT(orders.date, '%%b %%e, %%Y')) as orderDate,
          status.status AS itemStatus,
          IF(orders_products.order_products_id IS NULL or orders_products.order_products_id = '', '0', '1') as isOrderProduct,
          status.quantity AS quantity,
          IF(orders_products.skuid IS NULL or orders_products.skuid = '', status.itemno, orders_products.skuid) as skuid,
          IF(orders_products.unoptioned_skuid IS NULL or orders_products.unoptioned_skuid = '', LEFT(status.itemno, 6), orders_products.unoptioned_skuid) as baseSkuid,
          IF(orders_products.name IS NULL or orders_products.name = '', status.itemname, orders_products.name) as itemName,
          IF(orders_products.optioned_notes IS NULL or orders_products.optioned_notes = '', NULL, orders_products.optioned_notes) as optionedNotes,
          IF(orders_products.optioned_suffix IS NULL or orders_products.optioned_suffix = '', NULL, orders_products.optioned_suffix) as optionedSuffix,
          IF(orders_products.custom IS NULL or orders_products.custom = '', NULL, orders_products.custom) as personalization,
          IF(orders_products.price IS NULL or orders_products.price = '', '0.00', orders_products.price) as price,
          IF(orders_products.total_price IS NULL or orders_products.total_price = '', '0.00', orders_products.total_price) as totalPrice,
          status.shipmethod AS shipMethodCode,
          IF(order_ship_methods.order_ship_method_name IS NULL or order_ship_methods.order_ship_method_name = '', NULL, order_ship_methods.order_ship_method_name) as shipMethodName,
          IF(status.shipdate IS NULL, NULL, DATE_FORMAT(status.shipdate, '%%b %%e, %%Y')) as shipDate,
          IF(status.entry_date IS NULL, NULL, DATE_FORMAT(status.entry_date, '%%b %%e, %%Y')) as entryDate,
          status.shiptrack AS trackingNumber,
          status.smartLabel,
          IF(products.SMLIMG IS NULL or products.SMLIMG = '', SUBSTRING(status.itemno, 1, 6), products.SMLIMG) as itemThumb,
          products.INVENTORY as nla,
          products.SKUID as productExists,
          products.IS_GIFTWRAP as isGiftwrap,
          IF(products.options IS NULL or products.options = '', '0', '1') as hasOptions,
          IF(products.MAXQ IS NULL or products.MAXQ = '', '25', products.MAXQ) as maxq
        FROM status
        LEFT JOIN orders
        ON orders.order_id = SUBSTRING(status.ordno, 2, 9)
        LEFT JOIN orders_products ON orders_products.order_id = SUBSTRING(status.ordno, 2, 9)
        AND status.itemno = REPLACE(orders_products.skuid, '-', '')
        LEFT JOIN order_ship_methods ON status.shipmethod = order_ship_methods.order_ship_method_code
        LEFT JOIN products ON orders_products.unoptioned_skuid = products.SKUID
        WHERE status.ordno RLIKE %(orderid_rlike)s
        AND status.bill_zip RLIKE %(zip_rlike)s
      """
    else:
        query = """
        SELECT
          orders_products.order_id as orderId,
          orders.bill_fname as billingFirstName,
          orders.bill_lname as billingLastName,
          orders.bill_street as billingAddress1,
          orders.bill_street2 as billingAddress2,
          orders.bill_city as billingCity,
          orders.bill_state as billingState,
          orders.bill_postal_code as billingPostalCode,
          orders.bill_country as billingCountry,
          LOWER(orders.bill_email) as billingEmail,
          orders.ship_fname as shippingFirstName,
          orders.ship_lname as shippingLastName,
          orders.ship_street as shippingAddress1,
          orders.ship_street2 as shippingAddress2,
          orders.ship_city as shippingCity,
          orders.ship_state as shippingState,
          orders.ship_postal_code as shippingPostalCode,
          orders.gift_wrap as giftWrap,
          orders.gift_message as giftMessage,
          orders.comments as comments,
          orders.notes as notes,
          orders.payment_method as paymentMethod,
          orders.ship_method as shipMethod,
          orders.coupon_code as couponCode,
          orders.source_code as sourceCode,
          IF(orders.total_discount IS NULL or orders.total_discount = '', '0.00', orders.total_discount) as totalDiscount,
          IF(orders.total_subtotal IS NULL or orders.total_subtotal = '', '0.00', orders.total_subtotal) as totalSubtotal,
          IF(orders.total_shipping IS NULL or orders.total_shipping = '', '0.00', orders.total_shipping) as totalShipping,
          IF(orders.total_tax IS NULL or orders.total_tax = '', '0.00', orders.total_tax) as totalTax,
          IF(orders.total_credit IS NULL or orders.total_credit = '', '0.00', orders.total_credit) as totalCredit,
          IF(orders.total_order IS NULL or orders.total_order = '', '0.00', orders.total_order) as totalOrder,
          orders.date as 'date',
          DATE_FORMAT(orders.date, '%%b %%e, %%Y') as orderDate,
          IF(orders.date < DATE_SUB(NOW(), INTERVAL 90 DAY), 'Archived', 'Processing') as itemStatus,
          '1' as isOrderProduct,
          orders_products.quantity as quantity,
          orders_products.skuid as skuid,
          orders_products.unoptioned_skuid as baseSkuid,
          orders_products.name as itemName,
          orders_products.optioned_notes as optionedNotes,
          orders_products.optioned_suffix as optionedSuffix,
          orders_products.custom as personalization,
          IF(orders_products.price IS NULL or orders_products.price = '', '0.00', orders_products.price) as price,
          IF(orders_products.total_price IS NULL or orders_products.total_price = '', '0.00', orders_products.total_price) as totalPrice,
          orders.ship_method as shipMethodCode,
          IF(ship_methods_loop.ship_method_name IS NULL or ship_methods_loop.ship_method_name = '', NULL, ship_methods_loop.ship_method_name) as shipMethodName,
          NULL as shipDate,
          DATE_FORMAT(orders_products.date, '%%b %%e, %%Y') as entryDate,
          NULL as trackingNumber,
          NULL as smartLabel,
          products.SMLIMG as itemThumb,
          products.INVENTORY as nla,
          products.SKUID as productExists,
          products.IS_GIFTWRAP as isGiftwrap,
          IF(products.options IS NULL or products.options = '', '0', '1') as hasOptions,
          IF(products.MAXQ IS NULL or products.MAXQ = '', '25', products.MAXQ) as maxq
        FROM orders_products
        INNER JOIN orders ON orders_products.order_id = orders.order_id
        LEFT JOIN ship_methods_loop ON orders.ship_method = ship_methods_loop.ship_method_code
        LEFT JOIN products ON orders_products.unoptioned_skuid = products.SKUID
        WHERE orders_products.order_id = %(orderid)s
        AND orders.bill_postal_code RLIKE %(zip_rlike)s
      """
    q = DB.fetch_all(query, params)

    if not q or not "results" in q or not len(q["results"]):
        current_app.logger.error(f"problem loading order {query}")
        return {"success": False, "error": True, "errors": ["Problem finding your order.  Please contact us."]}

    # grab the order-level values out of the first result
    for order_field in order_fields:
        val = q["results"][0].get(order_field)
        if is_float(val):
            order[order_field] = float(val)
        elif is_int(val):
            order[order_field] = int(val)
        else:
            order[order_field] = val

    for res in q["results"]:
        item = {}
        for item_field in item_fields:
            v = res.get(item_field)
            if is_float(v):
                item[item_field] = float(v)
            elif is_int(v):
                item[item_field] = int(v)
            elif v and item_field == "personalization":
                j = None
                try:
                  j = json.loads(v)
                except JSONDecodeError as e:
                  current_app.logger.error(f"Problem decoding personalization: {e}")
                item[item_field] = j
            else:
                item[item_field] = v
        item["thumbPath"] = image_path(item.get("itemThumb"))
        item["trackingUrl"] = get_tracking_link(item["trackingNumber"], item["shipMethodCode"])
        order["items"].append(item)
    order["success"] = True
    order["error"] = False

    return {"order": order}
