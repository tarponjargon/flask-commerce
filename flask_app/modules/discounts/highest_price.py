from datetime import datetime
from flask import g, current_app
from copy import copy
from pprint import pprint
from flask_app.modules.helpers import is_number, format_currency


def apply_highest_priced_discount(discount=None):
    """Apply any active coupon-based highest-priced-item-in-cart promo

    Args:
      discount (dict): The discount object (loaded from 'discounts')

    NOTE: this mutates the cart item(s) directly using .set
    """

    if not discount:
        discount = {}

    now = datetime.now()

    # if found but expired
    start_time = discount.get("start_timestamp") if isinstance(discount.get("start_timestamp"), datetime) else datetime(1970, 1, 1)
    end_time = discount.get("end_timestamp") if isinstance(discount.get("end_timestamp"), datetime) else datetime(1970, 1, 1)

    if start_time > now:
      return None
    if end_time < now:
      return None

    # found but qty threshold (discount['order_min']) is not met
    if g.cart.get_quantities() < discount.get("order_min", 0):
        return None

    item = g.cart.get_highest_priced_item()
    if item:
        item_price = copy(item.get('price'))
        new_price = copy(item.get('price'))
        num = discount["discount"]

        # if the discount is a number and value is >1 it's a $-off discount
        if is_number(num) and float(num) > 1 and float(num) < item_price:
            new_price = item_price - float(num)

        # the discount is a percentage (0.10), apply %-off discount
        elif is_number(num) and float(num) < 1 and float(num) > 0:
            new_price = item_price * (1 - float(num))

        if new_price and new_price < item_price:

          # if the quantity is > 1, you have to modify the each price
          if item.get('quantity', 1) > 1:
            discount_amount = item.get('price') - new_price
            amortized_discount = discount_amount / item.get('quantity')
            adjusted_price = item.get('price') - amortized_discount
            item.set("price", adjusted_price)
            item.set("ppd1_price", item_price)
            item.set("is_tweaked", True)
            printable_savings = format_currency(discount_amount)
            item.set("promo_message", f"Item price modified to reflect discount off the first item. Savings: {printable_savings}")

          else:
              item.set("price", new_price)
              item.set("ppd1_price", item_price)
              item.set("is_tweaked", True)