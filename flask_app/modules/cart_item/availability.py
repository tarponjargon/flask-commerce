""" Functions related to item availability """

from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import invdata_faker

@cache.memoize()
def get_availability(fullskuid=None):
    """Determines a cart item's availability

    The query is somewhat complex, but has the complex business rules baked in

    There is a gotcha with inventory lookups.  See docstring for .helpers.invdata_faker

    Args:
      fullskuid (str): The full skuid of the cart item

    Returns:
      dict:
        code (str): 'instock', 'backordered', 'preorder', 'drop_ship', 'nla'
        description (str): Descrption of the availability type
        css_class (srt): The associated css class for availability
        schema_code (str): schema.org code
        lead_time (str): If the item is a drop ship, the lead time to shipment
    """
    availability = {"code": "", "description": "", "lead_time": "", "schema_code": "", "css_class": ""}

    if not fullskuid:
        return availability

    skuid = fullskuid.replace("-", "")

    query = """
      SELECT
          invdata.invcode AS invcode,
          invdata.is_preorder AS is_preorder,
          IF(invdata.dicontinuesflag = '1' AND (invdata.`count`+0 <= 0 OR invdata.invcode = 'S1'), 1, 0) AS nla,
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
        FROM invdata
        LEFT JOIN dropship_backorder ON invdata.skuid = dropship_backorder.fullsku
        WHERE invdata.skuid = %(skuid)s
        LIMIT 1
      """

    invdata_sql = invdata_faker(skuid, 'fullsku')
    if (invdata_sql):
      query = f"{invdata_sql} LIMIT 1"
      current_app.logger.info("FAKE CART AVAILABILITY SQL %s: %s", skuid, query)

    result = DB.fetch_one(query, {"skuid": skuid})
    if result:
        if result.get("nla"):
            availability["code"] = "nla"
            availability["description"] = "No longer available"
            availability["css_class"] = "text-danger"
            availability["schema_code"] = "https://schema.org/OutOfStock"

        elif result.get("is_preorder"):
            availability["code"] = "preorder"
            availability["description"] = f"Ships {result.get('backorder')}"
            availability["css_class"] = "text-danger"
            availability["schema_code"] = "https://schema.org/PreOrder"

        elif result.get("backorder"):
            availability["code"] = "backorder"
            availability["description"] = f"Available {result.get('backorder')}"
            availability["css_class"] = "text-danger"
            availability["schema_code"] = "https://schema.org/BackOrder"

        elif result.get("invcode") == "T1" or result.get("invcode") == "T2":
            availability["code"] = "drop_ship"
            availability["description"] = f"Ready to Ship"
            availability["lead_time"] = result.get("lead_time")
            availability["css_class"] = "text-dark"
            availability["schema_code"] = "https://schema.org/InStock"

        else:
            availability["code"] = "instock"
            availability["description"] = "In Stock &amp; Ready to Ship"
            availability["css_class"] = "text-success"
            availability["schema_code"] = "https://schema.org/InStock"

            if result.get("on_hand") < 11 and result.get("on_hand") > 0:
                availability["description"] = f"Hurry! Only {int(result.get('on_hand'))} left in stock."
                availability["css_class"] = "text-danger"

    return availability
