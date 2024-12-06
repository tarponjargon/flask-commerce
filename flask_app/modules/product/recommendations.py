""" Functions related to generating product recommendations"""

from pprint import pprint
import random
import urllib.parse
from datetime import datetime, timedelta
from flask import g, current_app, request
from flask_app.modules.helpers import validate_skuid
from flask_app.modules.product import Product
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import split_to_list, validate_skuid, image_path
from flask_app.modules.category.categories import get_category, get_parent_category
from flask_app.commands.feeds.master import get_origprice

def get_product_recommendations(skuid, analytics_id="", heading="You May Also Like", limit=12, exclude_skuids=[]):
  """ Get product recommendations for a given skuid

  Args:
    skuid (str): The SKU ID of the product
    analytics_id (str): The analytics ID
    heading (str): The heading for the recommendations
    link (str): The link for the recommendations
    limit (int): The number of recommendations to return
    exclude_skuids (list): A list of SKUIDs to exclude

  Returns:
    dict: A monetate-style recommendation object
  """

  if not exclude_skuids:
    exclude_skuids = []

  # start with some viewed products
  recs = get_viewed_products(4, exclude_skuids)
  exclude_viewed = [i.get('id') for i in recs]
  exclude_skuids.extend(exclude_viewed)
  recs_limit = limit - len(recs)
  recs.extend(get_related_products(skuid, recs_limit, exclude_skuids))
  shuffled_recs = random.sample(recs, len(recs))

  return {
    "actionId": "product",
    "id": f"{analytics_id} | {heading}",
    "recommendations": shuffled_recs
  }

def get_recommendations(analytics_id="", heading="You May Also Like", limit=12, exclude_skuids=[]):
  """ Get general recommendations

  Args:
    analytics_id (str): The analytics ID
    heading (str): The heading for the recommendations
    link (str): The link for the recommendations
    limit (int): The number of recommendations to return
    exclude_skuids (list): A list of SKUIDs to exclude

  Returns:
    dict: A monetate-style recommendation object
  """

  if not exclude_skuids:
    exclude_skuids = []

  # start with some viewed products
  recs = get_viewed_products(6, exclude_skuids)
  exclude_viewed = [i.get('id') for i in recs]
  exclude_skuids.extend(exclude_viewed)
  bestseller_limit = limit - len(recs)
  recs.extend(get_general_bestsellers(bestseller_limit, exclude_skuids))
  shuffled_recs = random.sample(recs, len(recs))

  return {
    "actionId": "recommendations",
    "id": f"{analytics_id} | {heading}",
    "recommendations": shuffled_recs
  }

def get_category_recommendations(category_code="", analytics_id="", limit=12, exclude_skuids=[]):
  """ Get recommendations for a specific category

  Args:
    category_code (str): The category code
    analytics_id (str): The analytics ID
    limit (int): The number of recommendations to return
    exclude_skuids (list): A list of SKUIDs to exclude

  Returns:
    dict: A monetate-style recommendation object
  """

  if not exclude_skuids:
    exclude_skuids = []

  category = get_category(category_code)
  if not category:
    return {}

  heading = category.get('category_name')
  link = category.get('path')
  recs = get_recs_from_category(category_code, exclude_skuids, limit)
  shuffled_recs = random.sample(recs, len(recs))

  return {
    "actionId": "category",
    "id": f"{analytics_id} | {heading} | {link}",
    "recommendations": shuffled_recs
  }

def create_monetate_product_object(product):
  """ Create a monetate-style product object from a Product object

  Args:
      product (Product): The product object

  Returns:
      dict: A monetate-style product object
  """

  if not product or not isinstance(product, Product):
      return {}

  image = None
  try:
    image = image_path(product.get('images', {}).get("image", ""), "regular")
  except:
    pass

  price = product.get("price")
  origprice = get_origprice(product)
  sale_price = None
  if origprice:
    sale_price = price
    price = origprice

  add_to_cart_link = f"/add?item={product.get('skuid')}"
  if product.has_options():
    add_to_cart_link = product.get("url")

  today = datetime.today().date()
  ninety_days_ago = today - timedelta(days=90)
  is_new = False
  try:
    is_new = product.get('creation_date') <= ninety_days_ago
  except:
    pass

  breadcrumb = product.get('default_category', {}).get('breadcrumb')
  breadcrumb_elements = breadcrumb.split(" > ") if breadcrumb else []

  return {
    "id": product.get("skuid"),
    "itemGroupId": product.get("skuid"),
    "title": product.get("name"),
    "imageLink": image,
    "addToCartLink": '/add?item=' + product.get("skuid"),
    "link": product.get("url"),
    "recToken": product.get("skuid"),
    "price": price,
    "salePrice": sale_price,
    "isPersonalized": True if product.get('custom') else False,
    "isClearance": any('clearance' in item['breadcrumb'].lower() for item in product.get('breadcrumb', [])),
    "rating": product.get("pr_rating"),
    "needsConfiguration": product.has_options(),
    "colorsAvailable": product.get("colorCount") if product.get("colorCount") else 0,
    "stylesAvailable": product.get("styleCount") if product.get("styleCount") else 0,
    "category1": breadcrumb_elements[0] if len(breadcrumb_elements) > 0 else "",
    "category2": breadcrumb_elements[1] if len(breadcrumb_elements) > 1 else "",
    "category3": breadcrumb_elements[2] if len(breadcrumb_elements) > 2 else "",
    "category4": breadcrumb_elements[3] if len(breadcrumb_elements) > 3 else "",
  }

def get_viewed_skuids_from_cookie():
  """ Get a list of SKUIDS that have been viewed

  Returns:
      list: A list of SKUIDs
  """

  cookie_val = urllib.parse.unquote(request.cookies.get('viewed_products', ""))
  if not cookie_val or not isinstance(cookie_val, str):
      return []
  skuids = split_to_list(cookie_val)
  if not skuids or not isinstance(skuids, list):
      return []
  skulist = []
  for skuid in skuids:
    if validate_skuid(skuid):
      skulist.append(skuid)
  return skulist

def get_viewed_products(limit=12, exclude_skuids=[]):
  """ Get recently viewed products.  SKUIDS are stored in a cookie
  Exclude anything in the cart

  Returns:
      list: A list of recently viewed products (product objects)
  """

  if not exclude_skuids:
    exclude_skuids = []

  viewed_skuids = get_viewed_skuids_from_cookie()
  if not viewed_skuids:
      return []

  filtered_viewed = [sku for sku in viewed_skuids if sku not in exclude_skuids]

  viewed_products = []
  shuffled_list = random.sample(filtered_viewed, len(filtered_viewed))
  for skuid in shuffled_list:
    viewed_product = Product.from_skuid(skuid)
    if not viewed_product or not viewed_product.get("featureable"):
      continue
    monetate_product = create_monetate_product_object(viewed_product)
    viewed_products.append(monetate_product)
    # current_app.logger.debug(f"Viewed product: {monetate_product.get('id')}")

  return viewed_products

def get_recs_from_category(category_code, exclude_skuids=[], limit=12):
  """ Query the database for for bestsellers from given category

  Args:
      category_code (str): The category code
      limit (int): The number of products to return

  Returns:
      list: A list of product objects
  """

  recs = []
  if not exclude_skuids:
    exclude_skuids = []

  if not category_code or not isinstance(category_code, str):
    return recs

  recs_query = f"""
      SELECT DISTINCT(skuid)
      FROM bestsellers_by_category
      WHERE category_code = %(category_code)s
      AND SKUID NOT LIKE '%%AV'
      AND SKUID NOT LIKE '%%AVDV'
      {'AND SKUID NOT IN %(exclude_skuids)s' if len(exclude_skuids) else ''}
      ORDER BY count DESC
      LIMIT %(limit)s
    """
  q = DB.fetch_all(recs_query, {
    'category_code': category_code,
    'exclude_skuids': exclude_skuids,
    'limit': abs(int(limit))
    })

  if not q or not "results" in q:
      return recs

  for prod in q['results']:
    rec = Product.from_skuid(prod['skuid'])
    if not rec or not rec.get("featureable"):
      continue
    monetate_rec = create_monetate_product_object(rec)
    # current_app.logger.debug(f"Category rec: {category_code} {monetate_rec.get('id')}")
    recs.append(monetate_rec)

  return recs

def get_general_bestsellers(limit=12, exclude_skuids=[]):
  """ Get general bestsellers for a product

  Returns:
      list: A list of general bestsellers
  """

  if not exclude_skuids:
    exclude_skuids = []
  bestsellers = []
  recs_query = f"""
        SELECT DISTINCT(skuid)
        FROM bestsellers_by_category
        WHERE SKUID NOT LIKE '%%AV'
        AND SKUID NOT LIKE '%%AVDV'
        {'AND SKUID NOT IN %(exclude_skuids)s' if len(exclude_skuids) else ''}
        ORDER BY count DESC
        LIMIT %(limit)s
      """
  q = DB.fetch_all(recs_query, {
    'exclude_skuids': exclude_skuids,
    'limit': abs(int(limit))
    })

  if not q or not "results" in q:
      return bestsellers

  for prod in q['results']:
    bestseller = Product.from_skuid(prod['skuid'])
    if not bestseller or not bestseller.get("featureable"):
      continue
    monetate_rec = create_monetate_product_object(bestseller)
    bestsellers.append(monetate_rec)
    # current_app.logger.debug(f"General bestseller: {monetate_rec.get('id')}")

  return bestsellers

def get_related_products(skuid, limit=12, exclude_skuids=[]):
    """Get product recommendations for a given skuid

    Args:
        skuid (str): The SKU ID of the product

    Returns:
        dict: A list of product objects
    """

    features_needed = limit
    related_products = []
    if not exclude_skuids:
        exclude_skuids = []
    if not validate_skuid(skuid):
        return related_products
    product = Product.from_skuid(skuid)
    if not product or not product.get("default_category"):
        return related_products
    default_category_code = product.get("default_category", {}).get("category_code")
    if not default_category_code:
        return related_products

    exclude_skuids.append(skuid)
    exclude_skuids.extend(g.cart.get_base_skuids())


    # Get bestsellers from the category
    related_products = get_recs_from_category(default_category_code, exclude_skuids, features_needed)

    features_needed = limit - len(related_products)

    # If we don't have enough, try parent category
    if features_needed > 0:
        parent_category = get_parent_category(default_category_code)
        if parent_category:
            related_products.extend(get_recs_from_category(parent_category.get("category_code"), exclude_skuids, limit))

    # if we still don't have enough, get general bestsellers
    features_needed = limit - len(related_products)
    if features_needed > 0:
        related_products.extend(get_general_bestsellers(features_needed))

    return related_products
