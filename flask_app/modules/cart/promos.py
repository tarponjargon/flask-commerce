""" Contains functions related to cart-level promotions """

from copy import copy


def apply_discount_by_type(price, discount_dict=None):
    """method shared by discounting functions

    handles 3 types of break discounts: direct price (1), percent off (2) and dollars off (3)

    Args:
      price (float): the price to be discounted
      discount_dict (dict): The discount to apply
        Example:
        {
          'discount': 32.95,
          'discount_type': 1
        }

    Returns:
      float: the discounted price

    """

    if discount_dict is None:
        discount_dict = {}

    current_price = price
    new_price = copy(current_price)

    # discount_type = 1 : the discount price is stated directly
    if (
        discount_dict["discount_type"] == 1
        and discount_dict["discount"] > 1
        and discount_dict["discount"] < current_price
    ):
        new_price = discount_dict["discount"]

    # discount_type = 2 : % off
    elif discount_dict["discount_type"] == 2 and discount_dict["discount"] < 1 and discount_dict["discount"] > 0:
        new_price = (current_price) * (1 - discount_dict["discount"])

    # discount_type = 3 : $ off
    elif (
        discount_dict["discount_type"] == 3
        and discount_dict["discount"] > 1
        and discount_dict["discount"] < current_price
    ):
        new_price = (current_price) - discount_dict["discount"]

    else:
        pass

    return float(new_price)
