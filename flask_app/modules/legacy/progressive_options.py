""" Functions related to multi-dimensional variant products """
from pprint import pprint
from flask import current_app, Response
from flask_app.modules.extensions import DB
from flask_app.modules.product import Product
from flask_app.modules.helpers import convert_to_ascii


def get_progressive_options(opref, lookupskuid):
    """
    Hazel has a custom action called "multi_option" that supports the old style UI for options selection
    for multi-dimensional products (more than 1 variant set).  When the first option is selected
    an AJAX call retrieves the available options for the next select menu.  A request looks like:

    /store?action=multi_option&OPTIONS_SET=HX4261_2&LOOKUPSKUID=HX4261BKTE&LOOKUPOPTION=BKTE

    The base skuid is not passed in this request, so it has to be deduced from the lookupskuid value (base_skuid+options_codes)
    then loading the variants themselves from product.variant_sets, then getting the inventory on each
    by checking variant_map.

    Args:
      opref (str): Comes in on the OPTIONS_SET request param.  the options set lives in product.OPTIONS delimited list and also the options.sku column
      lookupskuid: (str): The base skuid with any previously-selected options appended (no space)

    Returns:
      list: List of objects required by the UI
    """

    nextops = []
    # print("opref")
    # print(opref)
    # print("lookupskuid")
    # print(lookupskuid)
    if not opref or not lookupskuid:
        return nextops
    result = DB.fetch_one(
        f"SELECT skuid FROM options_index WHERE fullsku LIKE %(skuid_wildcard)s LIMIT 1",
        {"skuid_wildcard": convert_to_ascii(lookupskuid) + "%"},
    )
    if not result or not result["skuid"]:
        return nextops
    product = Product.from_skuid(result["skuid"])
    if not product or not product.get("variant_sets"):
        current_app.logger.error(f"No product or variant_sets found for lookupskuid: {lookupskuid} and opref: {opref}")
        return nextops
    opset = next((d for d in product.get("variant_sets") if d.get("option_set") == opref), None)
    # print("opset")
    # print(opset)

    if opset:
        for variant in opset.get("variants"):
            fullskuid = lookupskuid + variant.get("code")
            # print("fullskuid")
            # print(fullskuid)
            # print("variant_map")
            # print(product.get("variant_map"))
            vset = next((d for d in product.get("variant_map") if d.get("fullsku").startswith(fullskuid)), None)
            if vset:
                invmessage = vset.get("invmessage") if vset else ""
                invlevel = vset.get("invlevel") if vset else 9999
                disabled = "disabled" if vset and vset.get("invmessage") in current_app.config["NLA_CODES"] else ""
                nextops.append(
                    {
                        "optionValue": variant.get("code"),
                        "optionDisplay": variant.get("description") + f" ({invmessage})" if invmessage else "",
                        "optionAttribute": disabled,
                        "optionInvLevel": invlevel,
                        "optionPriceChange": float(variant.get("pricechange")),
                        "optionAvailMessage": " " + invmessage,
                    }
                )
    # pprint(nextops)
    return nextops
