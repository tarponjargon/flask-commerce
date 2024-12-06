""" Product route Blueprint

Flask Blueprint for rendering Product (PDP) HTML
"""

import re
import json
from pprint import pprint
from flask import Blueprint, render_template, current_app, redirect, request
from flask_app.modules.http import page_not_found
from flask_app.modules.helpers import validate_skuid
from flask_app.modules.extensions import DB, cache
from flask_app.modules.product import Product, get_skuid_by_path, get_path_by_skuid, get_parent_child_map
from flask_app.commands.feeds.master import CustomJSONEncoder


mod = Blueprint("product_view", __name__)

@cache.memoize()
def create_metadesc(product=None):
    if not product:
        product = {}
    metaprefix = "Find items like " + product.get("name")
    reviews_plural = "s" if product.get("pr_reviewcount", 0) > 1 else ""
    rating = str(product.get('pr_rating', 0)).replace('.0', '')
    reviews_text = (
        f"and read {product.get('pr_reviewcount')} review{reviews_plural} with a {rating}/5 star rating"
        if product.get("pr_reviewcount")
        else ""
    )
    metadesc = f"{metaprefix} {reviews_text} at {current_app.config['STORE_NAME']}. "
    if product.get("meta_desc_tag"):
      return product.get("meta_desc_tag")
    else:
      return metadesc + product.get("description", "")

@cache.memoize()
def get_related(skuid, group_id):
    related = []
    if not skuid or not group_id:
        return related
    if group_id:
        q = DB.fetch_all(
            """
              SELECT SKUID AS skuid
              FROM products
              WHERE GROUP_ID = %(group_id)s
              AND SKUID != %(skuid)s
              AND products.INVENTORY != 1
            """,
            {"group_id": group_id, "skuid": skuid},
        )
        if q and "results" in q:
            mapped = map(Product.from_skuid, [r["skuid"] for r in q["results"]])
            related = list(mapped)

    return related

@cache.memoize()
def redirect_to_parent(skuid):
  """ if a skuid is "slice" (a child that has sliced out into its own base product) of a parent product,
  redirect to the parent product with slice option(s) appended to the url so they can be preselected
  """

  # do not do anything if the SKU is *obviously* a base skuid
  if not skuid or not len(skuid) > 6:
    return ""

  # get an index of all parent-child relationships
  parent_index = get_parent_child_map()

  # gets the first match where the
  parent_skuid = next((i['parent'] for i in parent_index if i['child'].startswith(skuid)), None)

  if parent_skuid:
    product = Product.from_skuid(parent_skuid)
    if product and product.get("url") and product.get('variant_map'):
      parent_url = product.get("url")
      variant_url_params = []
      # get the first variant the child skuid startswith (or matches entirely)
      variant = next((x for x in product.get('variant_map') if x['fullsku'].startswith(skuid)), None)
      # loop the variant's code list and append to the parent url so I can
      # match each separate option built into the child product slice
      if variant and variant.get('code_list'):
        sku_builder = parent_skuid
        for index, code in enumerate(variant.get('code_list')):
          sku_builder = sku_builder + code
          if sku_builder == skuid:
            variant_url_params.append(f"OP{index + 1}={code}")
            break

      if variant_url_params:
        return f"{parent_url}?{'&'.join(variant_url_params)}"
      else:
        return parent_url

  return ""

@mod.route('/<regex("[0-9A-Za-z]{4,12}.[Hh][Tt][Mm][Ll]"):skupath>')
def do_product(skupath):
    """Routes matching this regex pattern are determined to be product URLs

    The SKUID is derived from the path.  Needs to account for possible case differences in the .html suffix
    """

    pattern = re.compile(r"\.html", re.IGNORECASE)
    skuid = pattern.sub("", skupath)
    if not validate_skuid(skuid):
        return page_not_found(None)

    # check if there is a slugified path for this product
    path = get_path_by_skuid(skuid)
    if path:
      qs = request.query_string.decode('utf-8')
      new_path = path
      if qs:
        new_path = f"{new_path}?{qs}"
      return redirect(current_app.config["STORE_URL"] + new_path, code=301)

    product = Product.from_skuid(skuid)
    if not product:
      return page_not_found(None)
    parent_redirect = redirect_to_parent(product.get('skuid', ""))
    if parent_redirect:
      return redirect(current_app.config["STORE_URL"] + parent_redirect, code=301)
    metadesc = create_metadesc(product) if product else ""
    if product and product.get_product():
        return render_template(
            "product.html.j2",
            product=product,
            metadesc=metadesc,
            related=get_related(product.get("skuid"), product.get("group_id")),
        )
    else:
        return page_not_found(None)

@mod.route('/products/<string:skupath>/<string:skuid>')
def do_product_slug(skupath, skuid):
  """ Product URLs """

  # if a newer path for the same product exists, redirect to the newer path
  skuid, newer_path = get_skuid_by_path(request.path)

  # current_app.logger.debug('skuid: {}, newer_path: {}'.format(skuid, newer_path))
  if newer_path:
    qs = request.query_string.decode('utf-8')
    new_path = newer_path
    if qs:
      new_path = f"{new_path}?{qs}"
    return redirect(current_app.config["STORE_URL"] + new_path, code=301)

  if not validate_skuid(skuid):
      return page_not_found(None)

  product = Product.from_skuid(skuid)
  if not product:
    return page_not_found(None)
  parent_redirect = redirect_to_parent(product.get('skuid', ""))
  if parent_redirect:
    return redirect(current_app.config["STORE_URL"] + parent_redirect, code=301)
  metadesc = create_metadesc(product) if product else ""
  if product and product.get_product():
      return render_template(
          "product.html.j2",
          product=product,
          metadesc=metadesc,
          related=get_related(product.get("skuid"), product.get("group_id")),
      )
  else:
      return page_not_found(None)
