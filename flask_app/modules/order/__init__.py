import re
import json
from flask import current_app, session
from flask_app.modules.cart_item import CartItem
from flask_app.modules.product import Product
from flask_app.modules.extensions import DB
from flask_app.modules.cart.shipping import get_method_descriptions
from flask_app.modules.checkout.order import is_post_order_offer_eligible
from flask_app.modules.product.images import get_image_by_fullskuid
from flask_app.modules.helpers import validate_email
from flask_app.modules.extensions import cache


@cache.memoize()
def get_payment_method_description(code):
    """Returns the full name for a given payment method code

    Args:
      code (str): The code to get the payment method description for

    Returns:
      str: A payment method description
    """
    q = DB.fetch_one(
        "SELECT pmt_method_name FROM payment_methods_loop WHERE pmt_method_code = %(code)s",
        {"code": code},
    )
    return q.get("pmt_method_name") if q.get("pmt_method_name") else code


def get_order_by_id(orderid):
    """Gets order by order id

    Args:
      orderid (str): The order ID, can be prefixed by a letter

    Returns:
      dict: The order
    """
    if not orderid or not re.match(r"^[A-Za-z]?[0-9]{6,9}", orderid):
        return {
            "success": False,
            "error": True,
            "errors": [
                f"Begins with an {current_app.config['ORDER_PREFIX']} followed by 7 numbers"
            ],
        }
    id = re.sub(r"[^0-9]", "", orderid)  # strip any letter prefix

    # load order from db
    order = DB.fetch_one(
        """
              SELECT *
              FROM orders
              WHERE order_id = %(orderid)s
            """,
        {"orderid": id},
    )

    # early return with error message if no order
    if not order:
        return {
            "success": False,
            "error": True,
            "errors": ["No order found"],
        }

    # load items from db
    order["items"] = []
    itemres = DB.fetch_all(
        """
            SELECT *
            FROM orders_products
            WHERE order_id = %(orderid)s
          """,
        {"orderid": id},
    )
    if itemres and "results" in itemres:
        for item in itemres["results"]:
            # load personalization json (if custom item)
            if item["custom"]:
                try:
                    item["personalization"] = json.loads(item.get("custom"))
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error decoding personalization: {e}")
                except ValueError as e:
                    print(f"ValueError decoding personalization: {e}")
                except TypeError as e:
                    print(f"TypeError decoding personalization: {e}")
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError decoding personalization: {e}")
                except AttributeError as e:
                    print(f"AttributeError decoding personalization: {e}")

            # prop65 warning
            if order.get("bill_state") == "CA" or order.get("ship_state") == "CA":
                item["prop65"] = CartItem.get_prop65_message(item.get("skuid"))

            item["product"] = Product.from_skuid(item.get("unoptioned_skuid"), False)
            item["image"] = get_image_by_fullskuid(item.get("skuid"))

            order["items"].append(item)

    # early return with error message if no items loaded
    if not len(order["items"]):
        return {
            "success": False,
            "error": True,
            "errors": [f"No items found for order"],
        }

    # load the selected ship method object (descriptions)
    shipmethods = get_method_descriptions()
    order["selected_method"] = next(
        (i for i in shipmethods if i["ship_method_code"] == order["ship_method"]), {}
    )

    order["payment_method_name"] = get_payment_method_description(
        order.get("payment_method")
    )

    # whether or not to show post-order offfer
    order["offer_eligible"] = is_post_order_offer_eligible(
        order.get("total_order"),
        order.get("bill_state"),
        order.get("bill_country"),
        order.get("bill_email"),
    )

    # split gfitmessage if exists - it sits in the field as a string list delimited by carats
    if order.get("gift_message"):
        gm = order.get("gift_message").split("^")
        order["gift_message1"] = gm[0] if len(gm) else ""
        order["gift_message2"] = gm[1] if len(gm) > 1 else ""
        order["gift_message3"] = gm[2] if len(gm) > 2 else ""
        order["gift_message4"] = gm[3] if len(gm) > 3 else ""
        order["gift_message5"] = gm[4] if len(gm) > 4 else ""
        order["gift_message6"] = gm[5] if len(gm) > 5 else ""

    return {"success": True, "error": False, "order": order}


def get_order_ids_by_email(email):
    """Get a list of order IDs given a customers e-mail address

    Args:
      email (str): The email to use for order lookup

    Returns:
      dict: A dictionary with success, error, errors and a list of order ID and dates
    """

    if not email or not validate_email(email):
        return {
            "success": False,
            "error": True,
            "errors": ["Please check e-mail format"],
        }

    orderres = DB.fetch_all(
        """
          SELECT order_id, date FROM orders WHERE bill_email LIKE %(email)s
        """,
        {"email": email},
    )

    if not orderres or "results" not in orderres or not len(orderres["results"]):
        return {
            "success": False,
            "error": True,
            "errors": ["No orders found"],
        }

    orders = []
    for order in orderres["results"]:
        orders.append(
            {
                "orderId": current_app.config["ORDER_PREFIX"]
                + str(order.get("order_id")),
                "date": order.get("date").strftime("%m/%d/%Y"),
            }
        )

    return {"success": True, "error": False, "orders": orders}


def delete_order_session_keys():
    # delete these keys from the session so they don't carry over to subsequent orders
    delete_keys = [
        "order_id",
        "credit_type",
        "credit_code",
        "credit_security_code",
        "credit_month",
        "credit_year",
        "card_type",
        "card_code",
        "card_security_code",
        "card_month",
        "card_year",
        "worldpay_registration_id",
        "worldpay_payment_token",
        "worldpay_vantiv_txn_id",
        "order_id",
        # "source_code",
        "comments",
        "gift_message",
        "gift_message1",
        "gift_message2",
        "gift_message3",
        "gift_message4",
        "gift_message5",
        "gift_message6",
        "giftcertificate",
        "gc_amt",
        "selectedskus",
        "fc_selected",
        "fc_selected2",
        "fc_selected2_qty",
        "fc_quantities",
        "coupon_code",
        "orig_coupon_code",
        "wpp_txn_id",
        "wpp_token",
        "wpp_payerid",
        "wpp_correlationid",
        "wpp_addressstatus",
        "wpp_paymentstatus",
        "wpp_payerstatus",
        "wpp_pendingreason",
        "wpp_tax",
        "wpp_total",
        "wpp_subtotal",
        "wpp_shipping",
        "payment_method",
        "checkoutpage",
        "howfound",
    ]
    for delete_key in delete_keys:
        session[delete_key] = None
