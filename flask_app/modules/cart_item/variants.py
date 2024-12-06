"""
A collection of functions related to item variants (options)
"""

import re
from pprint import pprint
from flask import current_app, g
from flask_app.modules.helpers import split_to_list, convert_to_ascii
from flask_app.modules.extensions import DB, cache


def get_variant_set(id):
    """Loads options with the options reference

    Args:
      id (str): The options reference, usually SKUID_n ex: HA7745_1

    Returns:
      dict: Dictionary containing metadata about the varients (like the set), and a list containing the variants themselses
    """

    variants = []
    variant_set = {}

    query = """
        SELECT
          options.id AS id,
          options.sku AS ref,
          options.code,
          options.description,
          options.pricechange,
          options.origprice_pricechange,
          options.tabletype AS type,
          option_types.name AS type_description,
          options.backorder,
          options.notstocked,
          options.image,
          options.sort_number
        FROM options
        LEFT JOIN option_types ON options.tabletype = option_types.code
        WHERE options.sku = %(id)s
        ORDER BY options.sort_number, options.id ASC
    """
    variants = DB.fetch_all(query, {"id": id})["results"]

    # 2024-04-19:  commented out since this doesn't seem to be relevant as the db column is a decimal
    # actually I can't find where this function even gets called
    # if variants:  # strip + signs out of pricehange
    #     # current_app.pretty(variants)
    #     for v in variants:
    #         try:
    #             v["pricechange"] = re.sub("[^0-9,.]", "", v["pricechange"])
    #         except Exception as e:
    #             pricechange = 0

    #     variant_set = {"id": id, "set_type": variants[0]["type"], "variants": variants}

    return variant_set


def get_variant_sets(ids):
    """Loads all variants using their variant set references

    Args:
      ids (str): the variant set or sets to load variants for.  If more than 1 they are semicolon
        delimited:  ex: HA1997_1;HA1997_2

    Returns:
      list: A list of all variants
    """

    if not ids:
        return []

    sets = None

    if isinstance(ids, str):
        sets = get_variant_ref_list(ids)
    if isinstance(ids, list):
        sets = ids
    # print("SETS", sets)
    if not sets:
        return []

    variants = [get_variant_set(id) for id in sets]

    return variants


def get_variant_map(skuid):
    """Gets a list of all valid ("legal") combinations of variants for given sku.
    An example is a shrit where sweatshirt, 3XL is a valid combo but t-shirt, 3XL isn't (because it's not offered)

    Args:
      skuid (str): The base skuid of the product to get variants for

    Returns:
      list: a list of all valid variant combinations for given sku
    """
    if not skuid:
        return None

    master_list = []
    query = """
        SELECT
          options_index.code_list,
          options_index.nla,
            IFNULL(`invdata`.`count`,9999) AS on_hand,
            `invdata`.`date` AS backorder_date,
            options_index.pricechange AS pricechanges,
            options_index.origprice_pricechange AS origprice_pricechanges,
            options_index.price
        FROM options_index
        LEFT JOIN invdata ON options_index.fullsku = invdata.skuid
        WHERE options_index.skuid = %(skuid)s
    """
    q = DB.fetch_all(query, {"skuid": skuid})
    if q and "results" in q and q["results"]:
        for result in q["results"]:
            code_list = split_to_list(result["code_list"])
            pricechanges = split_to_list(result["pricechanges"])
            pricechanges = [i for i in pricechanges]
            origprice_pricechanges = split_to_list(result["origprice_pricechanges"])
            origprice_pricechanges = [i for i in origprice_pricechanges]
            master_list.append(
                {
                    "fullskuid": skuid + "-" + "-".join(code_list),
                    "code_list": code_list,
                    "on_hand": int(result["on_hand"]),
                    "backorder_date": result["backorder_date"],
                    "pricechanges": pricechanges,
                    "origprice_pricechanges": origprice_pricechanges,
                    "price": result["price"],
                    "nla": int(result["nla"]),
                }
            )

    return master_list


def get_selected_variant_data(variant_codes=None, variant_ref_list=None):
    """takes a list of codes like 'S', 'RED' and a list of variant list keys like 'SB001_1','SB001_2'
    checks the options the descriptions and upcharges.  the codes and the list refs have to be in a
    corresponding order.  meaning 'S' needs to be in list SB001_1 and 'RED' in 'SB001_2'

    Args:
      variant_codes (list): The selected variant codes
      variant_ref_list (list): The options references

    Returns:
      dict: A dictionary containing a total of all variant upcharges, and a list of the variant descriptions
    """

    if variant_codes is None:
        variant_codes = []
    if variant_ref_list is None:
        variant_ref_list = []

    # loop through lists by index, and query options by each set + code, sum up pricechanges
    selected_variants = {"upcharge": 0.00, "origprice_upcharge": 0.00, "descriptions": []}
    for i in range(len(variant_ref_list)):
        query = """
                  SELECT
                    options.pricechange,
                    options.origprice_pricechange,
                    options.code,
                    options.description,
                    options.tabletype as tabletype,
                    option_types.name as option_type
                  FROM options
                  LEFT JOIN option_types ON options.tabletype = option_types.code
                  WHERE options.sku = %(options_sku)s
                  AND options.code = %(options_code)s
              """
        params = {"options_sku": variant_ref_list[i], "options_code": variant_codes[i]}
        result = DB.fetch_one(query, params)
        if result:
            try:
                pricechange = float(result["pricechange"])
            except Exception as e:
                pricechange = 0
            selected_variants["upcharge"] += pricechange
            try:
                origprice_pricechange = float(result["origprice_pricechange"])
            except Exception as e:
                origprice_pricechange = 0

            selected_variants["origprice_upcharge"] += origprice_pricechange

            variant_type = ""

            variant_type = result.get("option_type") if result.get("option_type") else result.get("tabletype")
            selected_variants["descriptions"].append(
                {
                    "code": result["code"],
                    "type": variant_type,
                    "description": re.sub(
                        r"\s?\([Aa]dd \$.*?\)", "", result["description"]
                    ),  # strips out "(Add $xx.xx)"
                    "upcharge": pricechange,
                    "origprice_upcharge": origprice_pricechange,
                }
            )
        else:
            return False
    return selected_variants


def get_variant_ref_list(base_skuid):
    """Gets a list of options references for given SKU

    Args:
      base_skuid (str): The base SKUID to get the options references for

    Returns:
      list: A list of options_references like ['SB001_1','SB001_2']
    """

    variant_ref_list = ""
    query = "SELECT OPTIONS from products WHERE skuid = %(base_skuid)s"
    result = DB.fetch_one(query, {"base_skuid": base_skuid})
    if result and result.get("OPTIONS"):
        variant_ref_list = split_to_list(result["OPTIONS"])

    return variant_ref_list


def check_optioned_available(fullskuid):
    """Checks availability for given fully-optioned (all veriants chosen) SKUID

    Args:
      fullskuid (str): The full skuid

    Returns:
      bool: True if the item is available, False if it is not
    """
    if not fullskuid:
        return False

    fullskuid = fullskuid.replace("-", "")
    available = False

    query = """
          SELECT nla
          FROM options_index
          WHERE fullsku = %(fullskuid)s
        """

    # print(query)
    try:
        result = DB.fetch_one(query, {"fullskuid": convert_to_ascii(fullskuid)})
        if result and "nla" in result:
            available = True if result["nla"] == "0" or result["nla"] == 0 else False
    except ValueError as e:
        current_app.logger.error(f"ERROR check_optioned_item_available function {e}")

    return available
