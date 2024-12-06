""" Functions related to a product's variants (options) """

from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import image_path, split_to_list, invdata_faker

@cache.memoize()
def get_variants_to_images(skuid):
    """Relates a product's variants to their specific variant images
    This relationship is not well-defined in the schema so it takes some heavy lifting

    Args:
      skuid (str): The base skuid of the product

    Returns:
      list: A list of dictionaries.  Each dictionary contains the variant data and image data

    Raises:
      ValueError: when something bad happens matching up variant and image
    """
    if not skuid:
        return []
    translation = []

    query = """
                SELECT
                    image_translation.base_skuid AS skuid,
                    image_translation.fullsku AS fullskuid,
                    image_translation.image,
                    options_index.code_list,
                    options_index.description,
                    options_index.tabletypes
                FROM image_translation
                LEFT JOIN options_index
                    ON options_index.skuid = image_translation.base_skuid
                    AND options_index.fullsku RLIKE image_translation.fullsku
                WHERE image_translation.base_skuid = %(skuid)s
                AND options_index.code_list IS NOT NULL
                GROUP BY image_translation.fullsku
                ORDER BY image_translation.id ASC
            """
    results = DB.fetch_all(query, {"skuid": skuid})["results"]
    if results:
        for i in results:
            # Looping thru the variant code list in each of these results and progressively concatenating
            # each code onto the sku until it matches the 'fullskuid' value.
            # this is because there can be variant matches on partially-optioned skus
            try:
                variant = {}
                if i["code_list"] and i["description"] and i["tabletypes"]:
                    code_list = split_to_list(i["code_list"])
                    desc_list = split_to_list(i["description"])
                    type_list = split_to_list(i["tabletypes"])
                    lstlen = len(code_list)
                    if len(desc_list) == lstlen and len(type_list) == lstlen:
                        accum = i["skuid"]
                        for idx, p in enumerate(code_list):
                            accum += p
                            if accum == i["fullskuid"]:
                                variant = {
                                    "code": code_list[idx],
                                    "type": type_list[idx].capitalize() if type_list[idx] else "",
                                    "description": desc_list[idx],
                                    "fullskuid": i["fullskuid"],
                                }
                                break
                translation.append(
                    {
                        "skuid": i["skuid"],
                        "fullskuid": i["fullskuid"],
                        "variant_data": variant,
                        "image": i["image"],
                        "images": {
                            "small": image_path(i["image"], "small"),
                            "regular": image_path(i["image"], "regular"),
                            "large": image_path(i["image"], "large"),
                            "zoom": image_path(i["image"], "zoom"),
                        },
                    }
                )
            except ValueError as e:
                current_app.logger.warning(f"ERROR get_variants_to_images {e}")
                continue

    return translation

@cache.memoize()
def get_variant_sets(options_ref=None):
    """Gets a list of variant objects

    Args:
      options_ref (str): The OPTIONS reference stored in the product record

    Returns:
      list: A list of dictionaries, each containing a variant object like "Color" (and associated colors)

    """
    variant_sets = []
    oprefs = split_to_list(options_ref)
    if not options_ref or not oprefs or not len(oprefs):
        return variant_sets

    for opref in oprefs:
        variants = DB.fetch_all(
            "SELECT * FROM options WHERE sku = %(opref)s ORDER BY sort_number,id", {"opref": opref}
        )["results"]
        if variants and len(variants):
            variant_sets.append(
                {"variants": variants, "option_type": get_option_type(variants[0]["tabletype"]), "option_set": opref}
            )

    return variant_sets

@cache.memoize()
def get_option_type(code=None):
    """Get the description (heading) for a variant set

    Args:
      code (str): The options code

    Returns:
      dict: the code and name

    """
    option_type = {"code": code, "name": ""}
    if not code:
        return option_type

    desc = DB.fetch_one("SELECT name FROM option_types WHERE code = %(code)s", {"code": code})
    if desc:
        option_type["name"] = desc["name"]
    else:
        if code.lower().startswith("size"):
            option_type["name"] = "Size"
        else:
            option_type["name"] = code

    return option_type

@cache.memoize()
def get_variant_map(product):
    """Gets a list of 'legal' variant combinations for a base skuid

    For filtering variant combinations in the user interface

    There is a gotcha with inventory lookups.  See docstring for .helpers.invdata_faker

    Example:
      Sweatshirt, M is 'legal'
      Baby Snapsuit, 3XL is not legal

    Args:
      product (dict): The product as a dictionary

    Returns:
      list: A list of dictionaries, each containing a fully-optioned, legal variant combination

    """
    if not product:
        return []
    variant_map = []

    skuid = product["skuid"]

    left_join_clause = "LEFT JOIN invdata ON options_index.fullsku = invdata.skuid"
    invdata_sql = invdata_faker(skuid, 'fullsku')
    if (invdata_sql):
      left_join_clause = f"""
        LEFT JOIN ({invdata_sql})
        AS invdata ON options_index.fullsku = invdata.skuid
      """
      current_app.logger.info("FAKE VARIANT SQL %s: %s", skuid, invdata_sql)

    # use a different left join for blank goods
    if product.get("blank_good"):
        left_join_clause = """
          LEFT JOIN blank_good_translation ON options_index.fullsku = blank_good_translation.whole_sku
          LEFT JOIN invdata ON blank_good_translation.record_40 = invdata.skuid
        """

    # yes, there is somewhat complex logic to determine an option's availability
    query = f"""
        SELECT
          options_index.skuid AS base_skuid,
          options_index.fullsku AS fullsku,
          options_index.tabletypes AS tabletypes,
          options_index.description AS descriptions,
          invdata.invcode AS invcode,
          options_index.code_list,
          IF(
            (invdata.dicontinuesflag = '1' AND (invdata.`count`+0)<=0) OR invdata.invcode = 'S1',
            1,
            0
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
          ) AS backorder,
          options_index.pricechange AS pricechanges,
          options_index.origprice_pricechange AS origprice_pricechanges,
          IF(options_index.price IS NOT NULL AND options_index.price != '', options_index.price, '0.00') AS price
        FROM options_index
        {left_join_clause}
        LEFT JOIN dropship_backorder ON options_index.fullsku = dropship_backorder.fullsku
        WHERE options_index.skuid = %(skuid)s
      """
    results = DB.fetch_all(query, {"skuid": skuid})["results"]
    for result in results:
        inventory_message = "Ready to Ship" if product.get("drop_ship") else "In Stock"
        if result["backorder"]:
            prefix = "Ships" if product.get("preorder") else "Available"
            inventory_message = f"{prefix} {result['backorder']}"
        codelist_dashed = result["code_list"].replace(";", "-")

        # add schema.org availability
        schema_code = "https://schema.org/InStock"
        if result["nla"]:
          schema_code = "https://schema.org/OutOfStock"
          inventory_message = "No Longer Available"
        if result["backorder"]:
          schema_code = "https://schema.org/BackOrder"
          if product.get("preorder"):
              schema_code = "https://schema.org/PreOrder"

        # find any variants_to_images entry by starting with the fully-optioned sku and subtracting options until found
        images = {}
        if result.get("code_list") and product.get("variants_to_images"):
            code_list = split_to_list(result["code_list"])
            for i in range(len(code_list), 0, -1):
                cl = code_list[:i]
                accum = product["skuid"] + "".join(cl)
                x = next((i for (i, d) in enumerate(product["variants_to_images"]) if accum == d["fullskuid"]), -1)
                if x > -1:
                    images = product["variants_to_images"][x].get("images", {})
                    break

        variant_map.append(
            {
                "backorder": result["backorder"],
                "code_list": split_to_list(result["code_list"]),
                "descriptions": split_to_list(result["descriptions"]),
                "types": split_to_list(result["tabletypes"]),
                "fullsku": result["fullsku"],
                "fullskuid": f"{product['skuid']}-{codelist_dashed}",
                "nla": result["nla"],
                "invlevel": result["on_hand"],
                "invmessage": inventory_message,
                "schema_code": schema_code,
                "invcode": result["invcode"],
                "price": result["price"],
                "pricechanges": split_to_list(result["pricechanges"]),
                "origprice_pricechanges": split_to_list(result["origprice_pricechanges"]),
                "images": images,
            }
        )

    return variant_map
