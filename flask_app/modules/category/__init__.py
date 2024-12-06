""" Category module

An instantiated Category class contains all category data.  Generally
called with the classmethod
"""

from flask import g, request
from flask_app.modules.category.categories import (
    get_breadcrumb,
    get_ld_json,
    get_category,
    get_parent_category,
    get_subcategories,
    get_category_products,
)
from flask_app.modules.preload import (
  get_search_state
)


class Category(object):
    def __init__(self, category_data=None):
        if category_data is None:
            category_data = {}

        self.data = category_data

    def get_category(self):
        """Gets category data as dictionary

        Returns:
          dict: The category as a dictionary
        """
        return self.data

    def get(self, key, default=None):
        """Generic getter for Category data dict

        Args:
          key (str): The key to get
          default (any): The value to return if key not found

        Returns:
          any: The value for the given key
        """
        return self.data.get(key, default)

    def get_path(self):
        """Gets category path

        Returns:
          str: The category path
        """
        return self.data.get("path")

    @classmethod
    def from_code(cls, category_code, detail=False):
        """Constructor creates Category object from code

        Args:
          category_code (str): The category code
          detail (bool): If True, also loads additional category data like parent, children and breadcrumb

        Returns:
          Category: the instantiated category object
        """
        category = get_category(category_code)

        if category and detail:
            category["parent"] = get_parent_category(category_code)
            category["children"] = get_subcategories(category_code)
            category["breadcrumb"] = get_breadcrumb(category_code)
            category["ld_json"] = get_ld_json(category["breadcrumb"])
            category["category_map"] = list(
                map(
                    lambda x: {
                      "name": x["category_name"],
                      "path": x["path"],
                      "items": x["hard_count"],
                      "level": x["level"]
                    },
                    get_subcategories(category_code, True),
                )
            )
            category["products"] = []
            category["pages"] = 0
            category["total_products"] = 0

            if not get_search_state():
                product_data = get_category_products(category_code, request.args.get("page", "0"))
                category["products"] = product_data["products"]
                category["pages"] = product_data["pages"]
                category["total_products"] = product_data["total_products"]

        return cls(category)
