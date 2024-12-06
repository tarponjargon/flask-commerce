""" Product module

An instantiated Product class contains all product data.  Generally it is
instantiated using the classmethod: Product.from_skuid(skuid), not directly
"""
from copy import copy
from datetime import datetime, date
from pprint import pprint
from flask import current_app, g
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import is_number, lowercase_keys
from flask_app.modules.product.tweak import tweak_product

@cache.memoize()
def get_skuid_by_path(path):
  """Get skuid from url path

  Args:
    path (str): The path

  Returns:
    tuple: The skuid and newer path (if exists)
  """

  # current_app.logger.debug('path: %s', path)
  # select the SKUID by path, and also the newer path if it exists
  res = DB.fetch_one("""
    SELECT
      t1.skuid AS skuid,
      (SELECT t2.path
      FROM product_urls t2
      WHERE t2.skuid = t1.skuid
        AND t2.timestamp > t1.timestamp
      ORDER BY t2.timestamp DESC, t2.id DESC
      LIMIT 1) AS newer_path
    FROM
      product_urls t1
    WHERE
      t1.path = %s;
  """, (path))

  # current_app.logger.debug('get_skuid_by_path: %s', res)

  return (res.get("skuid"), res.get("newer_path"))

@cache.memoize()
def get_path_by_skuid(skuid):
  """Get path for a given skuid

  Args:
    path (str): The skuid

  Returns:
    str: the path
  """

  res = DB.fetch_one("""
    SELECT path
    FROM product_urls
    WHERE skuid = %s
    ORDER BY timestamp DESC, id DESC
    LIMIT 1
  """, (skuid))

  return res.get("path")

@cache.memoize()
def get_parent_child_map():
    """ Get all parent-child relationships for all products

    Returns:
      dict:
      {
        'parent' : str
        'child' : list
      }
    """
    parent_index = {}
    options_query = DB.fetch_all(
        """
          SELECT skuid AS parent, fullsku AS child
          FROM options_index
        """
    )

    if options_query["results"]:
        parent_index = options_query["results"]

    return parent_index


class Product(object):
  def __init__(self, product_data=None):
      if product_data is None:
          product_data = {}

      self.data = product_data

  def get_product(self):
      """Product getter

      Returns:
        dict: The Product as dict
      """
      return self.data

  def get(self, key, default=None):
      """
      Get the given key on the product object

      Args:
        key (str): The key get on the product object
        default (any): The value to return of the key is not found

      Returns:
        any: The value for the given key or the default value
      """
      returnval = self.data.get(key)
      return returnval if returnval else default

  def get_origprice(self):
      """ Gets the original price of the product
      This may seem superfluous to .get('origprice') but please leave it

      Returns:
        float: The original price for the product
      """

      return self.get("origprice", 0.00)

  def set(self, key, value):
      """Generic setter for Product data dict

      Args:
        key (str): The key to add to the product data dictionary
        value (any): the value to set
      """
      self.data[key] = value

  def to_dict(self):
      """Get product as dict

      Returns:
        dict: The Product as dict
      """
      return self.data

  def is_custom_moonglow(self):
      """Determines if this product is a special personalized product that requires a custom personalization UI

      Returns:
        bool: True if it is a moonglow item, false if not
      """
      moonglow_skuids = [
          "HU2712",
          "HU2572",
          "HP7702",
          "HR3852",
          "HR3862",
          "HU1792",
          "HU1802",
          "HU2732",
          "HU2702",
          "HU2712",
          "HU2722",
          "HW6802",
          "HW8012",
          "HAZ962",
      ]
      return True if self.get("skuid").upper() in moonglow_skuids else False

  def is_custom_lake(self):
      """checks if the item is a 'Personalized Lake' item, which requires special personalization UI

      Returns:
        bool: True if it's a lake product, False if not
      """

      return True if "personalized lake" in self.get("name", "").lower() else False

  def get_rich_snippet(self):
      """Get ld+json for this product"""
      from flask_app.modules.product.ld_json import create_rich_snippet

      return create_rich_snippet(self.get_product())

  def has_options(self):
      """Checks if this product has options (variants)

      Returns:
        bool: True if the product has options, false if not
      """

      sets = self.get("variant_sets", [])
      return True if sets and len(sets) > 0 else False

  @classmethod
  def from_skuid(cls, skuid, detail=True):
      """Constructor creates Product object from skuid

      This is the recommended way to load a product

      Args:
        skuid (str): The product SKUID
        detail (bool): Whether or not to load the "full" product data (variants, etc)

      Returns:
        Product: the product object
      """

      if not skuid:
          return None

      from .variants import get_variants_to_images, get_variant_map, get_variant_sets
      from .images import get_images
      from .category import get_default_category, get_default_breadcrumb
      from .badges import get_badges
      from .price import has_pricerange
      from .availability import get_availability, is_waitlist
      from .metadata import get_drop_ship, get_alternate_ids, get_attributes, get_metadata
      from .personalization import get_personalization_prompts

      product = {}
      query = """
                  SELECT *
                  FROM products
                  WHERE SKUID = %(skuid)s
              """
      product_data = DB.fetch_one(query, {"skuid": skuid})

      # print("product_data", product_data)
      # print(product_data)

      if product_data:
          product_data = lowercase_keys(product_data)

          # enforce a proper date on creation_date field
          # TODO enforce this type/default value in DB schema
          if not product_data.get("creation_date") or not isinstance(product_data.get("creation_date"), date):
              product_data["creation_date"] = date(1970, 1, 1)

          # 'custom' can sometimes have a string value of '0' which should be falsey.  coerce that to None
          if product_data.get("custom") == "0":
              product_data["custom"] = None

          # if SHIPPING has a string value of '0' change it to '+0'
          if product_data.get("shipping") == "0":
              product_data["shipping"] = '+0'

          # trim the product name
          if product_data.get("name") and isinstance(product_data.get("name"), str):
              product_data["name"] = product_data.get("name").strip()

          if detail:
              # only load full product details if 'detail' is true
              alternate_ids = get_alternate_ids(skuid)
              product_data["mpn"] = alternate_ids.get("mpn")
              product_data["gtin"] = alternate_ids.get("gtin")
              product_data["brand"] = alternate_ids.get("brand")
              product_data["variants_to_images"] = get_variants_to_images(skuid)
              product_data["variant_map"] = get_variant_map(product_data)
              product_data["attributes"] = get_attributes(skuid)
              product_data["metadata"] = get_metadata(skuid)

          # default product data (in addition to the db data)
          product_data["is_waitlist"] = is_waitlist(skuid)
          product_data["pristine_price"] = copy(product_data["price"]) # product price can get modified, so we need to keep the original :(
          product_data["variant_sets"] = get_variant_sets(product_data["options"])
          product_data["availability"] = get_availability(skuid)
          product_data["drop_ship_type"] = get_drop_ship(product_data["drop_ship"])
          product_data["personalization"] = get_personalization_prompts(product_data["custom"])
          product_data["url"] = get_path_by_skuid(skuid) or f"/{skuid}.html"
          product_data["images"] = get_images(product_data)
          product_data["badges"] = get_badges(product_data)
          product_data["has_pricerange"] = has_pricerange(skuid)
          product_data["default_category"] = get_default_category(product_data)
          product_data["breadcrumb"] = get_default_breadcrumb(product_data)
          product_data["nla"] = product_data["inventory"] or product_data["is_waitlist"]

          # process any dynamic product-level tweaks
          product_data = tweak_product(product_data)

          product = product_data

      else:
          return None

      # print(product)

      return cls(product)
