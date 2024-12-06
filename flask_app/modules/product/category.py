""" Functions related to a product's categorization """

from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.category.categories import get_category, get_breadcrumb
from flask_app.modules.helpers import dedupe, split_to_list

def get_default_category(product):
    """Returns a default category object for a product

    Args:
      product (dict): The product to get the default category for

    Returns:
      dict: The default category
    """

    default_category = {}
    if not product or not isinstance(product, dict):
        return default_category

    # main category is not always specified. merge main_category and category
    # into a single list and get the first active one with items in it
    main = product.get("main_category", "")
    cats = product.get("category", "")
    category_codes = dedupe(split_to_list(f"{main};{cats}"))

    loopcount = 0
    for code in category_codes:
        loopcount += 1
        result = get_category(code)

        if result and result.get("category_code"):
            default_category = result
            break

        # never loop more than x
        if loopcount == 5:
            break

    return default_category


def get_default_breadcrumb(product):
    """Returns a default category breadcrumbtrail for a product

    Args:
      product (dict): The product to get the breadcrumb trail for

    Returns:
      list: A list of dictionaries
    """

    breadcrumb = []

    if not product or not isinstance(product, dict):
        return breadcrumb

    default_category = get_default_category(product)

    # return if not all required keys are in dict
    if not default_category or "category_code" not in default_category:
        return breadcrumb

    breadcrumb = get_breadcrumb(default_category["category_code"])

    return breadcrumb
