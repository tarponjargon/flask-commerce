""" Home page route and view helper functions"""
import re
import os.path
from flask import Blueprint, render_template, current_app, request, redirect
from flask_app.modules.banners import get_homepage_slides
from flask_app.modules.extensions import DB, cache
from urllib.parse import urlparse
from flask_app.modules.helpers import split_to_list, split_and_quote


mod = Blueprint("home_view", __name__)


@cache.memoize()
def get_homepage_banners():
    """Generates 6 feature banners for home page, occasionally referred to as the "6-pack"

    The source is the homepage_banners table.

    Returns:
      list: A list of 6 dictionaries, each containing the info needed to render the feature banner
    """
    banners = []
    sql = """
      SELECT filename, link, title, link_is_external
      FROM homepage_banners
      WHERE start_date < NOW() AND end_date > NOW()
      AND (filename IS NOT NULL AND filename !='')
      ORDER BY sort_order ASC, id ASC
      LIMIT 6"""
    results = DB.fetch_all(sql)["results"]
    for banner in results:
        banners.append(banner)

    return banners


def get_category_banners():
    """Generates 12 category feature banners for home page, occasionally referred to as the "12-pack"

    The source is the homepage_featured_categories table which contains titles and
    links, the image needs to be generated using some specific logic.

    First, defer to any skuids that are specified in the skuids field (can be multiple, semicolon delimited)
    If none or those are not FEATUREABLE, then tre to generate using bestsellers_by_category table.

    Returns:
      list: A list of 12 dictionaries, each containing the info needed to render the category banner
    """
    categories = []
    exclude = []
    query1 = "SELECT * FROM homepage_featured_categories ORDER BY sort_order ASC"
    results1 = DB.fetch_all(query1)["results"]
    for cat in results1:
        skuids = split_to_list(cat["skuids"])
        category = {"feature_image": "", "title": cat["title"], "link": cat["link"]}

        # first check if any skuids specified to feature.  If so, check feature-ability
        if cat["skuids"]:
            query2 = f"""
                        SELECT SKUID, SMLIMG FROM products
                        WHERE SKUID IN %(skuids)s
                        {'AND SMLIMG NOT IN %(exclude)s' if len(exclude) else ''}
                        AND INVENTORY != 1
                        AND FEATUREABLE = 1
                      """
            params = {"skuids": tuple(skuids), "skuids_str": split_and_quote(skuids), "exclude": tuple(exclude)}

            # go thru my pre-ordered skuids list and get the first matching db result
            # switched to this logic 1/10/24.  I was using ORDER BY FIELD(SKUID, [skuids]) in the sql but wasn't having expected results
            results2 = DB.fetch_all(query2, params)
            if results2 and len(results2["results"]):
              for sku in skuids:
                hit = next((m for m in results2["results"] if m.get("SKUID") == sku), None)
                if hit:
                  category["feature_image"] = hit["SMLIMG"]
                  break

        # if no feature sku specified, generate one from bestsellers for this specific category
        if not category["feature_image"]:
            possible_features = []
            category_code = ""
            try:
                mypath = urlparse(category["link"]).path
                category_code = os.path.basename(mypath)
            except Exception as e:
                current_app.logger.error(
                    f"Could not parse category from link for homepage_featured_categories id {cat['id']}"
                )
                continue

            query3 = """
                      SELECT skuid
                      FROM bestsellers_by_category
                      WHERE category_code = %(category_code)s
                      ORDER BY `count` DESC
                      LIMIT 6
                    """
            params = {"category_code": category_code}
            results3 = DB.fetch_all(query3, params)["results"]

            if not results3 or not len(results3):
              # occasionally it happens where there are no bestsellers for a category or the table itself is being refreshed
              query3 = """
                        SELECT skuid
                        FROM products_to_categories_loop
                        WHERE category_code = %(category_code)s
                        ORDER BY RAND()
                        LIMIT 6
                      """
              params = {"category_code": category_code}
              results3 = DB.fetch_all(query3, params)["results"]

            for item in results3:
                possible_features.append(item["skuid"])


            query4 = f"""
                        SELECT SMLIMG FROM products
                        WHERE SKUID IN %(possible_features)s
                        {'AND SMLIMG NOT IN %(exclude)s' if len(exclude) else ''}
                        AND INVENTORY != 1
                        AND FEATUREABLE = 1
                        ORDER BY RAND() LIMIT 1
                      """
            params = {"possible_features": tuple(possible_features), "exclude": tuple(exclude)}
            results4 = DB.fetch_all(query4, params)["results"]
            for image in results4:
                exclude.append(image["SMLIMG"])
                category["feature_image"] = image["SMLIMG"]

        categories.append(category)

    return categories


@mod.route("/")
def home_view():
    """Home page view"""
    return render_template(
        "home.html.j2",
        slides=get_homepage_slides(),
        banners=get_homepage_banners(),
        categories=get_category_banners(),
    )
