""" Functions that mutate the cart AFTER the cart is fully instantiated """

from flask import g, session, current_app
from flask_app.modules.preload import get_discounts
from flask_app.modules.http import session_get
from flask_app.modules.discounts.group_discount import apply_gdiscount
from flask_app.modules.discounts.club_discount import apply_club_discount
from flask_app.modules.discounts.item_level_qty import apply_item_level_qty_threshold
from flask_app.modules.discounts.highest_price import apply_highest_priced_discount
from flask_app.modules.discounts.free_gift import apply_free_gift
from flask_app.modules.discounts.buy_x import apply_buy_x
from flask_app.modules.discounts.group_min_spend import group_min_spend_discount
from flask_app.modules.discounts.messaging import apply_promo_message



def post_process_cart():
    """Called from Flask's after_request hook to modify the cart AFTER the full cart/cartitems are loaded"""

    # check for and apply any group/quantity discounts
    apply_gdiscount()

    # check if the product has a club discount
    if current_app.config.get('STORE_CODE') == 'basbleu2' and g.cart.is_club_validated():
      apply_club_discount()

    discount = get_coupon_discount()
    if discount:

        # if the discount is off the highest-priced item, it's processed here
        if discount.get("discount_type") == "7":
            apply_highest_priced_discount(discount)

        # if the promotion is a free gift, it's processed here
        if discount.get("discount_type") == "5":
            apply_free_gift(discount)

        # if the promotion is item-level qty threshold
        if discount.get("discount_type") in ["6","8"]:
            apply_item_level_qty_threshold(discount)

        # if the promotion is a buy x get 1
        if discount.get("discount_type") == "9":
            apply_buy_x(discount)

        # if the promo is group min spend to get item discount
        if discount.get("discount_type") == "11":
            group_min_spend_discount(discount)

        # the discount messaging aspect is somewhat decoupled from the actual redemption.
        # redemption can occur in the cart, in a cart_item tweak or in this module.
        # but messaging for all the coupon-driven promos always happens here.
        apply_promo_message()
        if 'promo' in g.messages and g.messages["promo"]:
          current_app.logger.debug("COUPON MESSAGE: " + g.messages["promo"])

    # Check if there's an employee discount.  if so apply restrictions to the order (EMPSHIP is excluded)
    code = session_get("source_code", session_get("coupon_code"))
    if code:
        code = code.upper()
        source_codes = [i["code"] for i in current_app.config["EMPLOYEE_DISCOUNTS"] if i["code"] != "EMPSHIP"]
        if code in source_codes:
            apply_employee_discount_rules(code)


def get_coupon_discount():
    """If there is a coupon code on the order, check against the "master" discounts index
    (loaded from the 'discounts' table) if found, send back the object

    Returns:
      dict: The discount object
    """

    coupon = g.promo_code

    if not coupon:
        return {}
    else:
        coupon = coupon.upper()

    discounts = get_discounts()

    # see if an active promo exists for given coupon code
    if coupon in discounts["index"]:
        return next((i for i in discounts["data"] if i.get("code") == coupon), {})

    return {}

def apply_employee_discount_rules(code):
    """Apply restrictions on orders with an employee discount (so that the code doesn't go viral)

    Args:
        code (str): The employee promotion code
    """

    # force a specific shipping address that correlates to the code being used
    discount = next((m for m in current_app.config["EMPLOYEE_DISCOUNTS"] if m.get("code") == code.upper()), None)
    session["shipSame"] = "no"
    if discount:
        for k, v in discount["address"].items():
            session[k] = v
