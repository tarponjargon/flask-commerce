""" Functions related to order placement """

import json
import re
from flask import current_app, g
from flask_app.modules.helpers import quote_list, get_order_notes
from flask_app.modules.http import get_env_vars, session_get
from flask_app.modules.extensions import DB
from flask_app.modules.preload import get_source_codes


def create_order_sql():
    """Create SQL for order row from session and cart data

    Returns:
      str: An INSERT SQL statement representing an order record
    """

    env_vars = get_env_vars()

    # concatenate gift message fields into one string demimited by carats
    # A legacy workaround for Pegasus allowing up to 6 20-char fields
    # strip out any special chars
    gift_message = ""
    if session_get("gift_message1"):
        gm1 = session_get("gift_message1", "")[:20]
        gm2 = session_get("gift_message2", "")[:20]
        gm3 = session_get("gift_message3", "")[:20]
        gm4 = session_get("gift_message4", "")[:20]
        gm5 = session_get("gift_message5", "")[:20]
        gm6 = session_get("gift_message6", "")[:20]

        gm1 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm1)
        gm2 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm2)
        gm3 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm3)
        gm4 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm4)
        gm5 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm5)
        gm6 = re.sub(r"[^0-9A-Za-z\.!\?&\(\)\-':,\+@ /]", "", gm6)

        gift_message = f"{gm1}^{gm2}^{gm3}^{gm4}^{gm5}^{gm6}"

    # if the item has a giftwrap SKU, create a specially-formatted giftwrap string
    # that gets decoded by the order download program
    gift_wrap = ""
    giftwrap_item = g.cart.get_giftwrap_item()
    if giftwrap_item:
        wrapped_key = "wrapped_" + giftwrap_item.get("skuid")
        if session_get(wrapped_key):
            gift_wrap = giftwrap_item.get("skuid") + ":" + session_get(wrapped_key)

    # make sure any entered source code is valid
    source_code = session_get("source_code", session_get("websource"))
    if source_code and source_code.upper() not in get_source_codes():
        source_code = ""

    # if no (valid) source code value and there is a websource value
    # validate that as a source code and if it passes, set it as the source code
    # 2023-12-29 added an exclusion rule...if the source code is a discount do not auto-add it.  it may result in double-dipping
    # AND decided to switch to sql to be consistent with current Hazel sites
    if not source_code and session_get("websource"):
        websource = session_get("websource", "").upper()
        # if websource in get_source_codes():
        #   source_code = websource
        q = DB.fetch_one(
            """
            SELECT count(*) as WS_COUNT
            FROM source_codes
            WHERE code = %(websource)s
            AND code NOT IN(
              SELECT code
              FROM discounts
              WHERE code = %(websource)s
              AND start_timestamp <= NOW()
              AND end_timestamp > NOW()
            )
          """,
            {"websource": websource},
        )
        if q and q["WS_COUNT"] == 1:
            source_code = websource

    # if there is no source code and there's a utm_medium=email, set the source code to config.DEFAULT_EMAIL_SOURCE
    if (
        not source_code
        and session_get("utm_medium", "") == "email"
        and current_app.config.get("DEFAULT_EMAIL_SOURCE")
    ):
        source_code = current_app.config.get("DEFAULT_EMAIL_SOURCE")

    order_sql = """
      INSERT INTO orders SET
        order_id = %(order_id)s,
        customer_id = %(customer_id)s,
        universal_uid = %(universal_uid)s,
        bill_fname = %(bill_fname)s,
        bill_lname = %(bill_lname)s,
        bill_street = %(bill_street)s,
        bill_street2 = %(bill_street2)s,
        bill_city = %(bill_city)s,
        bill_state = %(bill_state)s,
        bill_postal_code = %(bill_postal_code)s,
        bill_zip_4 = %(bill_zip_4)s,
        bill_country = %(bill_country)s,
        bill_email = %(bill_email)s,
        bill_phone = %(bill_phone)s,
        ship_fname = %(ship_fname)s,
        ship_lname = %(ship_lname)s,
        ship_street = %(ship_street)s,
        ship_street2 = %(ship_street2)s,
        ship_city = %(ship_city)s,
        ship_state = %(ship_state)s,
        ship_postal_code = %(ship_postal_code)s,
        ship_zip_4 = %(ship_zip_4)s,
        ship_country = %(ship_country)s,
        payment_method = %(payment_method)s,
        ship_method = %(ship_method)s,
        websource = %(websource)s,
        my_referer = %(my_referer)s,
        remote_addr = %(remote_addr)s,
        true_client_ip = %(true_client_ip)s,
        http_user_agent = %(user_agent)s,
        device_type = %(device_type)s,
        client = %(cart_id)s,
        source_code = %(source_code)s,
        origsource = %(origsource)s,
        coupon_code = %(coupon_code)s,
        orig_coupon_code = %(orig_coupon_code)s,
        backend_coupon = %(backend_coupon)s,
        giftcertificate = %(giftcertificate)s,
        howfound = %(howfound)s,
        howfound2 = %(howfound2)s,
        gift_message = %(gift_message)s,
        gift_wrap = %(gift_wrap)s,
        comments = %(comments)s,
        notes = %(notes)s,
        BBSVALIDATED = %(BBSVALIDATED)s,
        BBSMEMBER = %(BBSMEMBER)s,
        wpp_payerid = %(wpp_payerid)s,
        wpp_txn_id = %(wpp_txn_id)s,
        wpp_token = %(wpp_token)s,
        wpp_addressstatus = %(wpp_addressstatus)s,
        wpp_payerstatus = %(wpp_payerstatus)s,
        wpp_correlationid = %(wpp_correlationid)s,
        wpp_pendingreason = %(wpp_pendingreason)s,
        total_subtotal = %(total_subtotal)s,
        total_surcharge = %(total_surcharge)s,
        total_shipping = %(total_shipping)s,
        total_tax = %(total_tax)s,
        total_discount = %(total_discount)s,
        total_credit = %(total_credit)s,
        total_order = %(total_order)s,
        date = %(date)s
    """

    params = {
        "order_id": session_get("order_id", ""),
        "customer_id": session_get("customer_id", ""),
        "universal_uid": session_get("universal_uid", ""),
        "bill_fname": session_get("bill_fname", ""),
        "bill_lname": session_get("bill_lname", ""),
        "bill_street": session_get("bill_street", ""),
        "bill_street2": session_get("bill_street2", ""),
        "bill_city": session_get("bill_city", ""),
        "bill_state": session_get("bill_state", ""),
        "bill_postal_code": session_get("bill_postal_code", ""),
        "bill_zip_4": session_get("bill_zip_4", ""),
        "bill_country": session_get("bill_country", ""),
        "bill_email": session_get("bill_email", ""),
        "bill_phone": session_get("bill_phone", ""),
        "ship_fname": session_get("ship_fname", ""),
        "ship_lname": session_get("ship_lname", ""),
        "ship_street": session_get("ship_street", ""),
        "ship_street2": session_get("ship_street2", ""),
        "ship_city": session_get("ship_city", ""),
        "ship_state": session_get("ship_state", ""),
        "ship_postal_code": session_get("ship_postal_code", ""),
        "ship_zip_4": session_get("ship_zip_4", ""),
        "ship_country": session_get("ship_country", ""),
        "ship_method": session_get("ship_method", ""),
        "payment_method": session_get("payment_method", ""),
        "websource": session_get("websource", ""),
        "my_referer": session_get("my_referer", ""),
        "remote_addr": env_vars["remote_addr"],
        "true_client_ip": env_vars["true_client_ip"],
        "user_agent": env_vars["user_agent"],
        "device_type": env_vars["device_code"],
        "cart_id": env_vars["cart_id"],
        "source_code": source_code,
        "origsource": session_get("origsource", ""),
        "coupon_code": session_get("coupon_code", ""),
        "orig_coupon_code": session_get("orig_coupon_code", ""),
        "backend_coupon": session_get("backend_coupon", ""),
        "giftcertificate": session_get("giftcertificate", ""),
        "howfound": session_get("howfound", ""),
        "howfound2": session_get("howfound2", ""),
        "gift_message": gift_message,
        "gift_wrap": gift_wrap,
        "comments": session_get("comments", ""),
        "notes": "<br />".join(get_order_notes()),
        "BBSVALIDATED": session_get("BBSVALIDATED", ""),
        "BBSMEMBER": session_get("BBSMEMBER", ""),
        "wpp_payerid": session_get("wpp_payerid", ""),
        "wpp_txn_id": session_get("wpp_txn_id", ""),
        "wpp_token": session_get("wpp_token", ""),
        "wpp_addressstatus": session_get("wpp_addressstatus", ""),
        "wpp_payerstatus": session_get("wpp_payerstatus", ""),
        "wpp_correlationid": session_get("wpp_correlationid", ""),
        "wpp_pendingreason": session_get("wpp_pendingreason", ""),
        "total_subtotal": g.cart.get_subtotal(),
        "total_surcharge": g.cart.get_surcharge(),
        "total_shipping": g.cart.get_shipping(),
        "total_tax": g.cart.get_tax(),
        "total_discount": g.cart.get_discount(),
        "total_credit": g.cart.get_credit(),
        "total_order": g.cart.get_total(),
        "date": env_vars["date"],
        "exported": "NO",
        "rejected": "P",
    }

    # dynamtically create AES encryption SQL strings
    params["salt"] = current_app.config["RANDOM_STRING"]
    encrypt_fields = [
        "credit_type",  # these credit_* must be in the list BEFORE card_* fields
        "credit_code",
        "credit_security_code",
        "credit_month",
        "credit_year",
        "card_type",  # these card_* fields must be in the list AFTER the credit_* fields
        "card_code",
        "card_security_code",
        "card_month",
        "card_year",
        "worldpay_registration_id",
        "worldpay_payment_token",
        "worldpay_vantiv_txn_id",
    ]
    for f in encrypt_fields:
        if session_get(f):
            key = f
            val = session_get(key)

            # if credit data is collected directly (not thru worldpay) the credit data is in credit_* fields
            # for sql purposes, name them 'card_' fields but give them the VALUES from their corresponding credit_* fields
            if f.startswith("credit"):
                key = f.replace("credit", "card")
                val = session_get(f)

                # and the uin-masked card code and security code are in fields ending with _saved ex: credit_code_saved
                if "code" in f:
                    val = session_get(f + "_saved")

            if key in params:
                # current_app.logger.debug("{} is already in params {}".format(key, params))
                # skip it if it's already been set, this will allow the fallback
                # fields to take precedence if both fallback and worldpay data is in the session
                # and avoiud SQL duplicate field errors
                continue

            params[key] = val

            # current_app.logger.debug("KEY, NEW KEY, VAL: " + str(f) + " - " + str(key) + " - " + str(params[key]))
            order_sql = order_sql + f", {key} = AES_ENCRYPT(%({key})s,%(salt)s)"

    # current_app.logger.debug("SQL: " + str(params))
    return (order_sql, params)


def create_item_sql(item):
    """Create SQL for order item from CartItem

    Args:
      CartItem: The CartItem

    Returns:
      str: An INSERT SQL statement representing one cart item
    """

    optioned_suffix = "-".join(item.get("variant_codes", []))
    optioned_notes = ", ".join(
        [i.get("description") for i in item.get("variant_data", [])]
    )
    env_vars = get_env_vars()
    item_sql = """
      INSERT INTO orders_products SET
        order_id = %(order_id)s,
        skuid = %(skuid)s,
        quantity = %(quantity)s,
        unoptioned_skuid = %(unoptioned_skuid)s,
        optioned_suffix = %(optioned_suffix)s,
        name = %(name)s,
        options = %(options)s,
        optioned_notes = %(optioned_notes)s,
        price = %(price)s,
        total_price = %(total_price)s,
        custom = %(custom)s,
        date = %(date)s
    """

    params = {
        "order_id": session_get("order_id"),
        "skuid": item.get("skuid"),
        "quantity": item.get("quantity"),
        "unoptioned_skuid": item.get("unoptioned_skuid"),
        "optioned_suffix": optioned_suffix,
        "name": item.get("name"),
        "options": item.get("product", {}).get("options"),
        "optioned_notes": optioned_notes,
        "price": item.get("price"),
        "total_price": item.get_total_price(),
        "custom": (
            json.dumps(item.get("personalization"))
            if item.get("personalization")
            else ""
        ),
        "date": env_vars["date"],
    }
    return (item_sql, params)


def create_order():
    """Create an order based on session data, environment data, and cart data.
    Notably, this does NOT use MySQL transactions because 'orders' and 'orders_products'
    are MyISAM engine, not innoDB.  I re-created a home-rolled transaction system from hazel days.
    """

    error_response = {
        "success": False,
        "error": True,
        "errors": ["Problem adding order, please contact us"],
    }

    (order_sql, params) = create_order_sql()

    # insert the order
    order_row_id = DB.insert_query(order_sql, params)
    if not order_row_id:
        return error_response

    # insert items
    item_row_ids = []
    has_item_error = False
    for item in g.cart.get_items():
        (item_sql, params) = create_item_sql(item)
        item_record_id = DB.insert_query(item_sql, params)
        if item_record_id:
            item_row_ids.append(item_record_id)
        else:
            has_item_error = True
            break

    # if there's an item insert error, need to delete any inserted rows
    if has_item_error:
        current_app.logger.error("item insert error encountered")
        DB.delete_query(f"DELETE FROM orders WHERE id = {order_row_id}")
        if len(item_row_ids):
            DB.delete_query(
                f"DELETE FROM orders_products WHERE id IN({quote_list(item_row_ids)})"
            )
        return error_response

    current_app.logger.debug("added order in record " + str(order_row_id))
    current_app.logger.debug("orders_products IDs")
    current_app.logger.debug(item_row_ids)

    return {"success": True, "error": False}


def is_post_order_offer_eligible(total, state, country, email):
    """Determines if the order qualifies for the post-order offer

    Returns:
      bool: True if eligible, False if not
    """

    return False
