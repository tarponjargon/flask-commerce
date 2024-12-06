""" Functions related to creation of the product ld+json (schema.org rich snippet) """

from pprint import pprint
from flask import current_app
from datetime import datetime
from flask_app.modules.helpers import image_path, convert_to_ascii, strip_html
from flask_app.modules.product.metadata import get_gtin
from flask_app.modules.extensions import cache

def get_schema_type(variant_type):
  """Get the schema.org type for the variant type

  check "variesBy" section of https://developers.google.com/search/docs/appearance/structured-data/product-variants
  for supported variants.

  There is alot of guesswork here, a huge bucket being
  "pattern" which is a catch all for anything that doesn't fit the other types

  Args:
    variant_type (str): The variant type

  Returns:
    str: The schema.org type for the variant type
  """
  if not variant_type:
    return ""

  vtype = variant_type.lower()
  if [s for s in ['color','metal','brown','beige'] if s in vtype]:
    return "color"
  if [s for s in ['size','volume','maginification','glassmag','voltage','length','absorbency','elevation','weight','tension','compression'] if s in vtype]:
    return "size"
  if "gender" in vtype:
    return "suggestedGender"
  if "style" in vtype:
    return "pattern"
  if [s for s in ['material','garment','texture'] if s in vtype]:
    return "material"
  return "pattern"

def create_direct_link(fullskuid):
  """Create a direct link to the product such that it pre-selects options

  Args:
    fullskuid (str): The full skuid of the product
    example: "FD5572-N-BG-XLC"

  Returns:
    str: the FQDN with path and query parameters
  """

  url = current_app.config["STORE_URL"]
  if not fullskuid or not '-' in fullskuid:
    return url + '/' + fullskuid + ".html"

  # split fullskuid into a list
  parts = fullskuid.split('-')
  base_skuid = parts[0]
  options = parts[1:]

  # loop options with index
  qs_list = []
  for i, option in enumerate(options):
    qs_list.append(f"OP{i+1}={option}")

  return current_app.config["STORE_URL"] + "/" + base_skuid + ".html?" + "&".join(qs_list)

def create_optioned(data):
    """Create the ld+json rich snippet for a product with options

    Args:
      data (dict): The product data

    Returns:
      dict: The ld+json product object as dict
    """

    variants = data.get('variant_map', [])
    if not len(variants):
      return ""

    schema_types = [get_schema_type(i) for i in variants[0].get("types")]

    product = {
      "@context": "https://schema.org/",
      "@type": "ProductGroup",
      "name": data.get("name"),
      "description": convert_to_ascii(data.get("description")),
      "url": current_app.config["STORE_URL"] + data.get("url"),
      "brand": data.get("brand"),
      "productGroupID": data.get("skuid"),
      "variesBy": ['https://schema.org/' + i for i in schema_types],
      "hasVariant": []
    }
    for variant in variants:
      descs = variant.get("descriptions", [])
      image = variant.get('images', {}).get('regular', '') if isinstance(variant.get('images', {}), dict) else ''
      if not image:
        mypath = data.get("images", {}).get("image")
        if mypath:
          image = image_path(mypath, "regular")
      myvariant = {
        "@type": "Product",
        "name": " ".join(descs),
        "sku": variant.get("fullskuid"),
        "mpn": variant.get("fullskuid"),
        "gtin": get_gtin(variant.get("fullskuid")),
        "description": " ".join(descs) + " - " + convert_to_ascii(data.get("description")),
        "offers": {
          "@type": "Offer",
          "priceCurrency": "USD",
          "url": create_direct_link(variant.get("fullskuid")),
          "price": float(variant.get("price")),
          "availability": variant.get("schema_code"),
          "itemCondition": "https://schema.org/NewCondition",
        }
      }
      if image:
        myvariant['image'] = image
      for i, schema_type in enumerate(schema_types):
        myvariant[schema_type] = descs[i] if len(descs) > i else ""

      product['hasVariant'].append(myvariant)
    return product

def create_unoptioned(data):
    """Create the ld+json rich snippet for a product without options

    Args:
      data (dict): The product data

    Returns:
      dict: The ld+json product object as dict
    """
    images = []
    if data.get("images") and data["images"].get("gallery"):
        images = [image_path(i["image"], "large") for i in data["images"]["gallery"]]

    product =  {
            "@context": "http://schema.org/",
            "@type": "Product",
            "name": data.get("name"),
            "description": convert_to_ascii(data.get("description")),
            "sku": data.get("skuid"),
            "image": images,
            "gtin": data.get("gtin"),
            "mpn": data.get("mpn"),
            "brand": data.get("brand"),
            "offers": {
                "@type": "Offer",
                "url": current_app.config["STORE_URL"] + data.get("url"),
                "itemCondition": "https://schema.org/NewCondition",
                "priceCurrency": "USD",
                "price": float(data.get("price")),
                "availability": data.get("availability", {}).get("schema_code"),
            },
        }
    return product

@cache.memoize()
def create_rich_snippet(data):
    """Create the ld+json rich snippet for given product

    Args:
      data (dict): The product data

    Returns:
      dict: The ld+json object as dict
    """

    ld_json = {
        "product": create_optioned(data) if data.get("variant_map") else create_unoptioned(data),
        "breadcrumb": {
            "@context": "http://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": current_app.config["STORE_URL"]}
            ],
        },
    }

    # only add rating data if ther ARE ratings
    if data.get("pr_reviewcount", 0) > 0 and data.get("pr_rating", 0) > 0:
      ld_json['product']['aggregateRating'] = {
        "@type": "AggregateRating",
        "ratingValue": round(float(data.get("pr_rating")), 1),
        "reviewCount": int(data.get("pr_reviewcount"))
      }

    # add breadcrumbs to ld_json object
    if data.get("breadcrumb"):
        for i, breadcrumb in enumerate(data.get("breadcrumb")):
            ld_json["breadcrumb"]["itemListElement"].append(
                {
                    "@type": "ListItem",
                    "position": i + 2,
                    "name": breadcrumb.get("category_name"),
                    "item": current_app.config["STORE_URL"] + breadcrumb.get("path"),
                }
            )
        ld_json["breadcrumb"]["itemListElement"].append(
            {
                "@type": "ListItem",
                "position": len(ld_json["breadcrumb"]["itemListElement"]) + 1,
                "name": data.get("name"),
                "item": current_app.config["STORE_URL"] + data.get("url"),
            }
        )

    # add video
    if data.get("video_preview"):
        fmt_date = data.get("creation_date").strftime("%Y-%m-%d") + ' 00:00:00' if data.get("creation_date") else data.get("timestamp").strftime("%Y-%m-%d") + ' 00:00:00'
        ld_json["video"] = {
            "video": {
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": data.get("name"),
                "description": strip_html(data.get("description")),
                "embedUrl": data.get("video_preview"),
                "uploadDate": fmt_date,
                "thumbnailUrl": image_path(data.get("smlimg")),
            }
        }

    # pprint(ld_json)
    return ld_json
