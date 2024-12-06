""" Functions related to getting product availability """

from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import split_and_quote, invdata_faker

@cache.memoize()
def get_availability(skuid=None):
    """Determines a base product's availability

    The query is somewhat complex, but has the complex business rules baked in

    There is a gotcha with inventory lookups.  See docstring for .helpers.invdata_faker

    Args:
      skuid (str): The base skuid

    Returns:
      dict:
        code (str): 'instock', 'backordered', 'preorder', 'drop_ship', 'nla'
        description (str): Descrption of the availability type
        css_class (srt): The associated css class for availability
        schema_code (str): schema.org code
        lead_time (str): If the item is a drop ship, the lead time to shipment
    """
    availability = {"code": "", "description": "", "lead_time": "", "schema_code": "", "css_class": ""}

    left_join_clause = "LEFT JOIN invdata ON products.skuid = invdata.skuid"
    invdata_sql = invdata_faker(skuid, 'skuid')
    if (invdata_sql):
      left_join_clause = f"""
        LEFT JOIN ({invdata_sql})
        AS invdata ON products.skuid = invdata.skuid
      """
      current_app.logger.info("FAKE PRODUCT AVAILABILITY SQL %s: %s", skuid, invdata_sql)

    query = f"""
      SELECT
          products.skuid AS base_skuid,
          products.options AS options,
          products.drop_ship AS drop_ship,
          drop_ship_type.description AS lead_time,
          invdata.invcode AS invcode,
          invdata.is_preorder AS is_preorder,
          IF(
            products.inventory = 1,
            1,
            IF(
              (invdata.dicontinuesflag = '1' AND (invdata.`count`+0 <= 0 OR invdata.invcode = 'S1'))
              OR (invdata.is_waitlist = 1 AND invdata.invcode REGEXP '^R'),
              1,
              0
            )
          ) AS nla,
          IF(`invdata`.`count` IS NOT NULL AND `invdata`.`count` != '', `invdata`.`count`+0, 9999) AS on_hand,
          IF(
            invdata.`date` IS NOT NULL AND invdata.`date` != '',
            invdata.`date`,
            IF(
              dropship_backorder.backorder_date IS NOT NULL AND dropship_backorder.backorder_date>=NOW(),
              DATE_FORMAT(dropship_backorder.backorder_date,'%%m/%%d') COLLATE utf8mb4_unicode_ci,
              NULL
            )
          ) AS backorder
        FROM products
        {left_join_clause}
        LEFT JOIN dropship_backorder ON products.skuid = dropship_backorder.fullsku
        LEFT JOIN drop_ship_type ON products.drop_ship = drop_ship_type.id
        WHERE products.skuid = %(skuid)s
        LIMIT 1
      """

    result = DB.fetch_one(query, {"skuid": skuid})
    # current_app.logger.debug("result: %s", result)
    if result:
      if is_waitlist(result.get("base_skuid")):
        availability["code"] = "nla"
        availability["description"] = "Coming Soon"
        if result.get("backorder"):
          availability["description"] = f"Estimated Arrival {result.get('backorder')}"
        availability["css_class"] = "text-danger"
        availability["schema_code"] = "https://schema.org/OutOfStock"

        return availability

      if result.get("nla"):
        availability["code"] = "nla"
        availability["description"] = "No longer available"
        availability["css_class"] = "text-danger"
        availability["schema_code"] = "https://schema.org/OutOfStock"

        return availability

      if result.get("is_preorder"):
        availability["code"] = "preorder"
        availability["description"] = f"Ships {result.get('backorder')}"
        availability["css_class"] = "text-danger"
        availability["schema_code"] = "https://schema.org/PreOrder"

        return availability

      if result.get("backorder"):
        availability["code"] = "backorder"
        availability["description"] = f"Available {result.get('backorder')}"
        availability["css_class"] = "text-danger"
        availability["schema_code"] = "https://schema.org/BackOrder"

        return availability

      if result.get("drop_ship"):
        availability["code"] = "drop_ship"
        availability["description"] = f"Ready to Ship"
        availability["lead_time"] = result.get("lead_time")
        availability["css_class"] = "text-dark"
        availability["schema_code"] = "https://schema.org/InStock"

        return availability

      if result.get("options") and ";" in result.get("options"):
        availability["code"] = "instock"
        availability["description"] = "Select options for availability"
        availability["css_class"] = "text-dark"
        availability["schema_code"] = "https://schema.org/InStock"

        return availability

      # default to in stock if nothing matched
      availability["code"] = "instock"
      availability["description"] = "In Stock &amp; Ready to Ship"
      availability["css_class"] = "text-success"
      availability["schema_code"] = "https://schema.org/InStock"

      if result.get("on_hand") < 11 and result.get("on_hand") > 0:
          availability["description"] = f"Hurry! Only {int(result.get('on_hand'))} left in stock."
          availability["css_class"] = "text-danger"

      if not result.get("nla") and result.get("options"):
          sql = f"""
          SELECT count(*) AS has_backordered
          FROM options
          WHERE sku IN({split_and_quote(result.get('options'))})
          AND (backorder IS NOT NULL AND backorder != '')
        """
          res = DB.fetch_one(sql)
          if res:
            if res.get("has_backordered"):
              availability["code"] = "instock"
              availability["description"] = "See options for availability"
              availability["css_class"] = "text-dark"
              availability["schema_code"] = "https://schema.org/InStock"

    return availability

@cache.memoize()
def is_waitlist(base_skuid):
    """Checks if the product meets the criteria for "wait list"
    It needs to be designated as waitlist-able AND also out of stock

    Args:
      base_skuid (str): The base skuid of the product to check

    Returns:
      bool: True if the product meets the criteria for waitlist, False if not
    """
    if not base_skuid:
        return False

    # added 7/12/24 waitlist flag is no in invdata as is_waitlist
    q = DB.fetch_all(
        """
          SELECT is_waitlist, invcode
          FROM invdata
          WHERE skuid LIKE %(base_skuid_wildcard)s
        """,
        {"base_skuid_wildcard": base_skuid + "%"},
    )

    if q and q.get("results"):
        nla = current_app.config["NLA_CODES"]
        # added 7/12/24 per alana's request, codes beginning with "R" can be wai-list items
        waitlisted = []
        for i in q.get("results"):
          if i["invcode"] in nla or 'R' in i["invcode"]:
            if i["is_waitlist"]:
                waitlisted.append(i)

        # if the results filtered for waitlist=yes and NLA is the same length as the results,
        # all children are waitlisted and item is designated as waitlist-able
        if len(waitlisted) == len(q.get("results")):
          return True

    return False
