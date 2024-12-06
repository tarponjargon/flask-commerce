""" Functions related to category data """

import math
from copy import deepcopy
from flask import current_app, request
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import split_to_list, is_int, convert_to_ascii
from flask_app.modules.product import Product
from pprint import pprint


@cache.memoize()
def get_category(category_code, exclude_empty=True):
    """Get category by category code
    Args:
      category_code (str): The category code

    Returns:
      dict: The category
    """

    exclude = "AND hard_count > 0" if exclude_empty else ""
    return DB.fetch_one(
        f"SELECT * FROM categories_loop WHERE category_code = %(category_code)s {exclude}",
        {"category_code": convert_to_ascii(category_code)},
    )


@cache.memoize()
def get_subcategories(category_code, nested=False):
    """Get a list of subcategories for given category code

    Args:
      category_code (str): The parent category code
      nested (bool): Whether or not to include the children of children (only 1 level allowed)

    Returns:
      list: List of dictionaries containing category url and category name
    """
    categories = []
    query = """
              SELECT * FROM categories_loop
              WHERE category_parent = %(category_code)s
              AND count > 0
              AND desktop_visible = 1
              ORDER BY sort_order ASC
            """
    q = DB.fetch_all(
        query,
        {"category_code": category_code})
    if (q.get('results')):
      for result in q["results"]:
        result['level'] = 0
        categories.append(result)

        if nested:
          r = DB.fetch_all(query, {"category_code": result['category_code']})
          if (r.get('results')):
            for res in r["results"]:
              res['level'] = 1
              categories.append(res)

    return categories

@cache.memoize()
def get_all_category_menu():
    """Get a list of categories and subcategories used for the main nav menu

    Returns:
      list: List of dictionaries representing records that are in desktop_nav_all
    """
    return DB.fetch_all(
        "SELECT * FROM desktop_nav_all WHERE is_visible = 1 ORDER BY column_num ASC, sort_order ASC, id ASC",
    )["results"]

@cache.memoize()
def get_parent_category(category_code):
    """Get the parent category for given category code

    Args:
      category_code (str): the category code to get parent for

    Returns:
      dict: The parent category
    """
    parent_category = {}
    curr = DB.fetch_one(
        "SELECT * FROM categories_loop WHERE category_code = %(category_code)s LIMIT 1",
        {"category_code": category_code},
    )
    if curr and curr["category_parent"]:
        parent_category = DB.fetch_one(
            "SELECT * FROM categories_loop WHERE category_code = %(category_parent)s LIMIT 1",
            {"category_parent": curr["category_parent"]},
        )
    return parent_category


@cache.memoize()
def get_breadcrumb(category_code):
    """Get the breadcrumb trail to given category

    Args:
      category_code (str): the category code to get the breadcrumb trail to

    Returns:
      list: A list containing the breadcrumb trail, the given category being last
    """
    # set default category is the first element

    current_parent = None
    top = current_app.config["ROOT_CATEGORY"]
    current_category = get_category(category_code, False)
    breadcrumb = [current_category]
    current_parent = current_category.get("category_parent")

    # If this is not already a top-level category, walk the tree UP to the top
    if not current_parent == top:

        loopcount = 0
        while True:
            loopcount += 1
            result = get_category(current_parent, False)

            # break out if no result or we've reached the max tries
            if not result or loopcount == 5:
                break

            else:
                breadcrumb.append(result)

                # break out of loop if at the top
                if result.get("category_code", "") == top or result.get("category_parent", "") == top:
                    break
                else:
                    # current_code = result["category_code"]
                    current_parent = result["category_parent"]

    # this function walked UP the tree and breadcrumb trails trails go DOWN, reverse the list
    if len(breadcrumb) > 1:
        breadcrumb = list(reversed(breadcrumb))

    return breadcrumb


@cache.memoize()
def get_breadcrumb_string(breadcrumbs, delim=" > "):
    """Create a string of breadcrumbs delimited by caret (or passed delimiter)
    Args:
      breadcrumbs (list): A list of the category objects
      delim (str): The delimiter to use between category names (default " > ")

    Returns:
      str: The breadcrumb trail as a string
    """
    bct = ""
    if not breadcrumbs or not isinstance(breadcrumbs, list):
        return bct

    lst = [i["category_name"] for i in breadcrumbs if "category_name" in i]
    if len(lst):
        bct = delim.join(lst)

    return bct


@cache.memoize()
def get_ld_json(breadcrumbs):
    """Create BreadcrumbList ld+json (schema.org rich snippet)

    Args:
      breadcrumbs (list): A list of the category objects

    Returns:
      dict: The BreadcrumbList ld+json as dict
    """
    ld_json = {
        "@context": "http://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": current_app.config["STORE_URL"]}
        ],
    }
    for i, breadcrumb in enumerate(breadcrumbs):
        ld_json["itemListElement"].append(
            {
                "@type": "ListItem",
                "position": i + 2,
                "name": breadcrumb.get("category_name"),
                "item": current_app.config["STORE_URL"] + breadcrumb.get("path"),
            }
        )

    return ld_json


@cache.memoize()
def get_root_categories():
    """Gets all the top-level category codes

    Returns:
      list: A list of the root-level category codes
    """
    root_categories = DB.fetch_all(
        """SELECT
          TRIM(category_code) AS category_code
          FROM categories_loop
          WHERE category_parent = %(root_category)s
        """,
        {"root_category": current_app.config["ROOT_CATEGORY"]},
    )["results"]
    return [i["category_code"] for i in root_categories]


@cache.memoize()
def get_desktop_nav():
    """Get categories to be shown in heading navigation on desktop

    Returns:
      list: a list of dictionaries, each being a distinct category dict from DB
    """
    nav = []
    # I'm doing the start/end date evaluation in SQL to avoid having to use datetime in python
    q = DB.fetch_all("""
      SELECT
        id,
        codes,
        name,
        rows_per_column,
        multi_level,
        IF(((banner_start_date IS NULL OR banner_start_date = 000000000000) OR banner_start_date < NOW()) AND ((banner_end_date IS NULL OR banner_end_date = 000000000000) OR banner_end_date > NOW()), banner_image, NULL) AS banner_image,
        IF(((banner_start_date IS NULL OR banner_start_date = 000000000000) OR banner_start_date < NOW()) AND ((banner_end_date IS NULL OR banner_end_date = 000000000000) OR banner_end_date > NOW()), banner_link, NULL) AS banner_link,
        IF(((banner_start_date IS NULL OR banner_start_date = 000000000000) OR banner_start_date < NOW()) AND ((banner_end_date IS NULL OR banner_end_date = 000000000000) OR banner_end_date > NOW()), banner_text, NULL) AS banner_text,
        IF(((banner_start_date2 IS NULL OR banner_start_date2 = 000000000000) OR banner_start_date2 < NOW()) AND ((banner_end_date2 IS NULL OR banner_end_date2 = 000000000000) OR banner_end_date2 > NOW()), banner_image2, NULL) AS banner_image2,
        IF(((banner_start_date2 IS NULL OR banner_start_date2 = 000000000000) OR banner_start_date2 < NOW()) AND ((banner_end_date2 IS NULL OR banner_end_date2 = 000000000000) OR banner_end_date2 > NOW()), banner_link2, NULL) AS banner_link2,
        IF(((banner_start_date2 IS NULL OR banner_start_date2 = 000000000000) OR banner_start_date2 < NOW()) AND ((banner_end_date2 IS NULL OR banner_end_date2 = 000000000000) OR banner_end_date2 > NOW()), banner_text2, NULL) AS banner_text2,
        sort_order,
        timestamp
      FROM nav_categories_desktop
      ORDER BY sort_order ASC, id ASC
    """)
    if q and "results" in q:
        for result in q["results"]:
            data = deepcopy(result)
            category_codes = split_to_list(result["codes"])
            data['categories'] = []
            for code in category_codes:
              # data["categories"] = [get_category(i) for i in category_codes]
              category = get_category(code)
              category['subcategories'] = get_subcategories(code, True)
              data["categories"].append(category)
            nav.append(data)
    # current_app.logger.debug(nav)
    return nav


@cache.memoize()
def get_mobile_nav():
    """Get categories to be shown in mobile navigation

    Returns:
      list: a list of dictionaries, each being a distinct category dict from DB
    """
    nav = []
    q = DB.fetch_all(
        """
          SELECT
            category_code,
            category_name,
            count,hard_count,
            path
          FROM categories_loop
          WHERE mobile_flyout_category > 0
          ORDER BY mobile_flyout_category ASC, sort_order ASC, id ASC
        """
    )
    if q and "results" in q:
        nav = q["results"]

    return nav


@cache.memoize()
def get_mobile_heading_nav():
    """Get categories to be shown in heading on mobile

    Returns:
      list: a list of dictionaries, each being a distinct category dict from DB
    """
    nav = []
    q = DB.fetch_all(
        """
          SELECT category_code, category_name, path
          FROM categories_loop
          WHERE mobile_heading_category > 0
          ORDER BY mobile_heading_category ASC, sort_order ASC, id ASC
        """
    )
    if q and "results" in q:
        nav = q["results"]

    return nav


@cache.memoize()
def get_category_products(category_code, page_num="0"):
    """Get the products for given category code

    Args:
      category_code (str): the category code to get products for

    Returns:
      list: List of Product objects
    """

    page = int(int(page_num) - 1) if is_int(page_num) and int(page_num) > 1 else 0
    start = page * current_app.config["PRODUCTS_PER_PAGE"]
    query = """
          SELECT SQL_CALC_FOUND_ROWS
            skuid
          FROM bestsellers_by_category
          WHERE category_code = %(category_code)s
          ORDER BY `count` DESC
          LIMIT %(start)s, %(per_page)s
        """
    params = {"category_code": category_code, "start": start, "per_page": current_app.config["PRODUCTS_PER_PAGE"]}
    q = DB.fetch_all(query, params)
    products = []

    if q and "results" in q:
        for result in q.get("results"):
            products.append(Product.from_skuid(result["skuid"]))

    total_products = q.get("calc_rows") if q else 0
    pages = math.ceil(total_products / current_app.config["PRODUCTS_PER_PAGE"])

    data = {"products": products, "total_products": total_products, "pages": pages}
    return data
