""" Search module

An instantiated Search class contains all search data.  Generally
called with the classmethod
"""

import math
from flask import g, request, current_app
from flask_app.modules.extensions import DB
from flask_app.modules.product import Product
from flask_app.modules.helpers import is_int, convert_to_ascii


class Search(object):
    def __init__(self, search_data=None):
        if search_data is None:
            search_data = {}

        self.data = search_data

    def get_search(self):
        """Gets search data as dictionary

        Returns:
          dict: The search as a dictionary
        """
        return self.data

    @classmethod
    def from_term(cls, term):
        """Constructor creates Search object from search term

        Args:
          term (str): The search term

        Returns:
          Search: the instantiated search object
        """

        page_num = request.args.get("page", "1")
        page = int(int(page_num) - 1) if is_int(page_num) and int(page_num) > 1 else 0
        start = page * current_app.config["PRODUCTS_PER_PAGE"]
        term = convert_to_ascii(term.strip())
        term = term.replace('%', '')

        if not term:
          return cls({"products": [], "total_products": 0, "pages": 0})

        query = """
                  SELECT SQL_CALC_FOUND_ROWS
                    skuid
                  FROM `products`
                  WHERE (
                    SKUID LIKE %(term_wildcard)s
                    OR NAME LIKE %(term_wildcard)s
                    OR KEYWORDS LIKE %(term_wildcard)s
                  )
                  AND INVENTORY+0 != 1
                  LIMIT %(start)s, %(per_page)s
                """
        params = {
            "term_wildcard": "%" + term + "%",
            "start": start,
            "per_page": current_app.config["PRODUCTS_PER_PAGE"],
        }
        q = DB.fetch_all(query, params)
        products = []

        if q and "results" in q:
            for result in q.get("results"):
                products.append(Product.from_skuid(result["skuid"]))

        total_products = q.get("calc_rows") if q else 0
        pages = math.ceil(total_products / current_app.config["PRODUCTS_PER_PAGE"])

        data = {"products": products, "total_products": total_products, "pages": pages}

        return cls(data)
