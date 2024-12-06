""" API routes for product """

import json
from pprint import pprint
from flask import Blueprint, request, Response
from flask import current_app
from flask_app.modules.helpers import sanitize, serialize, validate_skuid
from flask_app.modules.product import Product
from flask_app.modules.product.recommendations import (get_product_recommendations,  get_recommendations, get_category_recommendations)
from flask_app.modules.legacy.progressive_options import get_progressive_options

mod = Blueprint("product_api", __name__, url_prefix="/api")

@mod.route("/product/<string:skuid>")
def do_product(skuid):
    """Returns a product as a JSON object"""
    if not validate_skuid(skuid):
        return { 'error': True, 'message': "Not found" }, 404
    product = Product.from_skuid(skuid, True)
    if not product:
        return { 'error': True, 'message': "Not found" }, 404
    return serialize(product.get_product())


@mod.route("/multioption")
def do_progressive_options():
    """A legacy method for multi-options selection still in use on quick-add/tax estimate"""
    opref = request.args.get("OPTIONS_SET")
    lookupskuid = request.args.get("LOOKUPSKUID")
    ops = get_progressive_options(opref, lookupskuid)
    # workaround for Flask not allowing lists as the top level in json
    return Response(json.dumps(ops), mimetype="application/json")

@mod.route("/product/recommendations", methods=["POST"])
def do_product_recs():
    """Returns a JSON object of product recommendations based on what the JSON payload asks for

    JSON Payload:
    {
      "skuid": "12345",
      "analytics_id": "Recommendations 1: PDP",
      "heading": "You May Also Like"
    }

    We removed Monetate recommendations but I want to leverage the front-end infrustracture we have in place for recommendations.
    I want to use the same JSON structure that Monetate uses for recommendations. This will allow us to easily switch back to Monetate if we need to.

    possible headings:
    You May Also Like - (Popcart, PDP, PLP)
    Complete Your Purchase With These Items (Cart)
    You Might Like (Error Page)
    Customers Also Viewed / Customers Also Bought (Error Page)
    Can't find what you're looking for? What about these instead?
    Bestsellers Hot Sellers (Error Page, Home Page)
    """

    recommendations = []
    exclude_skuids = []
    payload = request.get_json()
    # current_app.logger.debug(f"Recommendations payload: {payload}")
    for rec_line in payload:
      recs_set = []
      skuid = sanitize(rec_line.get("skuid", ""))
      category_code = sanitize(rec_line.get("category", ""))
      analytics_id = sanitize(rec_line.get("reportingId", ""))
      heading = sanitize(rec_line.get("title", ""))
      limit = sanitize(rec_line.get("maxResults", 12))

      if rec_line.get("recommendationsType") == 'product' and validate_skuid(skuid):
        recs_set = get_product_recommendations(skuid, analytics_id, heading, limit, exclude_skuids)
      elif rec_line.get("recommendationsType") == 'recommendations':
        recs_set = get_recommendations(analytics_id, heading, limit, exclude_skuids)
      elif rec_line.get("recommendationsType") == 'category' and category_code:
        recs_set = get_category_recommendations(category_code, analytics_id, limit, exclude_skuids)

      # if a set of recs is found, add the skus to exclude_skuids so none of them will be recommended again if more than
      # one set is shown on the page
      if recs_set:
        exclude_skuids = [i.get('id') for i in recs_set.get('recommendations', []) ]
        recommendations.append(recs_set)

    return recommendations[:limit]

