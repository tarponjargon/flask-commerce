"""
Creates a master feed for a brand.  THis uses the google schema
https://support.google.com/merchants/answer/7052112
"""

import json
import os
import re
from decimal import Decimal
from pprint import pprint
from flask import current_app
from datetime import datetime, date, timedelta
from collections import OrderedDict
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import (
  convert_to_ascii,
  image_path,
  reformat_datestring,
  is_number,
  strip_non_numeric,
  split_to_list
)
from flask_app.modules.product import Product
from flask_app.modules.cart_item import CartItem
from flask_app.modules.product.ld_json import get_schema_type
from flask_app.modules.product.metadata import get_vendor, get_gtin

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

def get_sales_rank(base_skuid):
  """Get the sales rank for a product

  Args:
    base_skuid (str): The base skuid

  Returns:
    int: The sales rank
  """
  q = DB.fetch_one("""
    SELECT `count` AS salesrank FROM sales_rank WHERE skuid = %s
  """, (base_skuid,))
  return q.get('salesrank') if q else None

def get_metadata_value(key, skuid, default=None):
  """Get the metadata value for a given skuid and column name (key)

  Args:
    key (str): The metadata key
    skuid (str): The skuid

  Returns:
    str: The metadata value
  """
  skuid = skuid.replace("-", "")
  q = DB.fetch_one(f"""
    SELECT TRIM({DB.esc(key)}) AS value
    FROM product_metadata
    WHERE fullsku = %s
  """, (skuid))
  return q.get('value') if q else default

def get_invdata_value(key, skuid, default=None):
  """Get the invdata value for a given skuid and column name (key)

  Args:
    key (str): The invdata key
    skuid (str): The skuid

  Returns:
    str: The invdata value
  """
  skuid = skuid.replace("-", "")
  q = DB.fetch_one(f"""
    SELECT TRIM({DB.esc(key)}) AS value
    FROM invdata
    WHERE skuid = %s
  """, (skuid))
  return q.get('value') if q else default


def get_attributes(skuid):
  """Get the product attributes for a given sku

  Args:
    skuid (str): The skuid

  Returns:
    dict: The product attributes
  """
  q = DB.fetch_all("""
    SELECT attribute_name, attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_value != 'na'
  """, (skuid,))['results']
  attributes = {}
  for attr in q:
    attributes[attr.get('attribute_name')] = attr.get('attribute_value')
  return attributes

def get_categories(product):
  """Get the product type for a product, which is the breadcrumb
  product type can be a concatenation of the breadcrumb categories

  Args:
    product (Product): The product object

  Returns:
    str: The product type
  """

  categories = ""
  breadcrumbs = []
  for breadcrumb in product.get("breadcrumb", []):
    breadcrumbs.append(breadcrumb.get("breadcrumb", ""))
  return breadcrumbs

def get_image_by_index(gallery, index):
  """ safely get an image path from a gallery

  Args:
    gallery (list): The product image gallery list
    index (int): The index of the image to get

  Returns:
    str: The image path or an empty string
  """
  if not gallery:
    gallery = []

  if index < len(gallery):
    imagepath = ""
    try:
      imagepath = image_path(gallery[index].get("image", ""), "large").replace('cdn-cgi/image/quality=65,format=auto/', '')
    except IndexError:
      return ""
    except AttributeError:
      return ""
    return imagepath
  else:
    return ""

def get_alternate_images(gallery):
  """ alternate images are the images in the gallery AFTER index 0

  Args:
    gallery (list): The product image gallery list

  Returns:
    list: The alternate image paths
  """
  if not gallery:
    gallery = []

  if not len(gallery) > 1:
    return []

  images = []
  for i in range(1, len(gallery)):
    imagepath = image_path(gallery[i].get("image"), "large").replace('cdn-cgi/image/quality=65,format=auto/', '')
    images.append(imagepath)

  return images


def availability_translate(schema_code):
  """Translate the availability code to a google schema code

  Args:
    schema_code (str): The schema.org availability url

  Returns:
    str: The google schema code
  """

  if schema_code == "https://schema.org/InStock":
    return "in_stock"
  elif schema_code == "https://schema.org/BackOrder":
    return "backorder"
  elif schema_code == "https://schema.org/PreOrder":
    return "preorder"
  elif schema_code == "https://schema.org/OutOfStock":
    return "out_of_stock"
  else:
    return "in_stock"

def format_availability_date(datestring):
  """Format the availability date string

  Args:
    datestring (str): The date string

  Returns:
    str: The formatted date string
  """
  return datetime.strptime(datestring, "%Y%m%d").strftime("%Y-%m-%d")

def get_origprice(product):
  """Get the original price for a product

  Args:
    product (Product): The product object

  Returns:
    float: the origprice
  """
  origprice = 0.00
  if product.get("ppd1_price") and is_number(product.get("ppd1_price")) \
    and product.get("ppd1_price") > product.get("price"):
    origprice = float(product.get("ppd1_price"))
  if product.get("origprice") and is_number(product.get("origprice")) \
    and product.get("origprice") > product.get("price"):
    origprice = float(product.get("origprice"))

  return origprice

def get_age_group(product, fullskuid):
  """Get the age group for a product.

  Args:
    product (Product): The product object
    fullskuid (str): The full skuid without dashes

  Returns:
    str: The age group (google schema)
  """

  age_group = None

  # now check product_attributes table this is the most reliable source
  q = DB.fetch_one("""
    SELECT attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name = 'age group'
  """, (fullskuid,))
  if q and q.get('attribute_value'):
    attr_val = q.get('attribute_value').lower()
    if 'adult' in attr_val:
      age_group = 'adult'
    elif 'kids' in attr_val:
      age_group = 'kids'
    elif 'toddler' in attr_val:
      age_group = 'toddler'
    elif 'infant' in attr_val or 'baby' in attr_val:
      age_group = 'infant'

  # if none found, do some munging on options
  if not age_group:
    for variant in product.get('variant_map', []):
      #pprint(variant)
      #print('--------------------------------------------- ')
      adult_sizes = ['S', 'M', 'L', 'XL', 'XL', 'XXL', '2XL', '2X', '3XL', '3X', '4X' 'XXXL' '4XL', '5XL', '5X', 'SM']
      code_list = variant.get('code_list')
      vlist = variant.get('descriptions')
      vdescs = ' '.join(vlist).lower()
      if variant.get('fullsku') == fullskuid and any(item.lower() in [x.lower() for x in code_list] for item in adult_sizes):
        age_group = 'adult'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'toddler' in vdescs:
        age_group = 'toddler'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and ('2t' in vdescs or '3t' in vdescs or '4t' in vdescs):
        age_group = 'toddler'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'child' in vdescs:
        age_group = 'kids'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'kid' in vdescs:
        age_group = 'kids'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'months' in vdescs:
        age_group = 'infant'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'baby' in vdescs:
        age_group = 'infant'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'infant' in vdescs:
        age_group = 'infant'
        # pprint(variant)
        break
      if variant.get('fullsku') == fullskuid and 'newborn' in vdescs:
        age_group = 'infant'
        # pprint(variant)
        break

  # if none found, check the product's categorization
  if not age_group:
    if any("women" in c.get('breadcrumb').lower() for c in product.get("breadcrumb", [])):
      age_group = "adult"
    if any("Men" in c.get('breadcrumb') for c in product.get("breadcrumb", [])):
      age_group = "adult"
    if any("children" in c.get('breadcrumb').lower() for c in product.get("breadcrumb", [])):
      age_group = "kids"
    if any("kids" in c.get('breadcrumb').lower() for c in product.get("breadcrumb", [])):
      age_group = "kids"
    if any("baby" in c.get('breadcrumb').lower() for c in product.get("breadcrumb", [])):
      age_group = "infant"

  # if none found check the PEGCAT (least reliable)
  if not age_group:
    # check the product's PEGCAT field first
    cat = product.get('pegcat', '')
    children = [
      "APPAREL > CHILDREN'S APPAREL",
      "ACORN DVD > CHILDRENS","SHIRTS > VENDOR CHILDREN & INFANTS",
      "Recreation/Fun - Plush & Dolls",
      "RECREATION/FUN > PLUSH & DOLLS",
      "RECREATION/FUN > GAMES",
      "RECREATION/FUN > HOBBIES & KITS"
    ]
    infant = ["RECREATION/FUN > BABY"]
    if any(cat.lower() == x.lower() for x in children):
      age_group = "kids"
    elif any(cat.lower() == x.lower() for x in infant):
      age_group = "infant"

  # if still nothing take a scattershot approach by scanning all the variant sets
  if not age_group:
    for vset in product.get("variant_sets", []):
      if any(" months" in c.get('description').lower() for c in vset.get("variants", [])):
        age_group = "infant"
        break
      if any("newborn" in c.get('description').lower() for c in vset.get("variants", [])):
        age_group = "infant"
      if any("2T" in c.get('description').lower() for c in vset.get("variants", [])):
        age_group = "toddler"
        break

  if not age_group:
    age_group = 'adult'
  return age_group

def get_shipping_override(price, shipping):
  """Get the shipping cost for a product when there is an extra shipping cost
  for this item (large/heavy).

  Args:
    price (float or str): The product price
    shipping (str): The shipping cost string

  Returns:
    str: The shipping cost + " USD" if there is one, else an empty string
  """
  shipping_cost = 0.00
  product_cost = float(price)
  extra_shipping = 0.00
  if shipping:
    tmp_shipping = strip_non_numeric(shipping)
    if is_number(tmp_shipping) and float(tmp_shipping) > 0:
      extra_shipping = float(tmp_shipping)
    else:
      return None
  else:
    return None

  total_cost = round(product_cost, 2)
  q = DB.fetch_one("""
    SELECT shipping_cost
    FROM standard_rates_loop
    WHERE order_max+0 >= %s
    AND order_min+0 <= %s
  """, (total_cost, total_cost))
  if q:
    shipping_cost = float(q['shipping_cost']) + extra_shipping

  return round(shipping_cost, 2) if shipping_cost > 0 else None

def translate_option_types(variant):
  """Translate the option types FROM our wacky wild-west descriptions
  TO a google-friendly keyword

  Args:
    variant (dict): The variant object

  Returns:
    dict: The translated option types
  """
  option_types = {}
  for i, optype in enumerate(variant.get('types', [])):
    try:
      option_types[get_schema_type(optype)] = variant.get('descriptions')[i]
    except IndexError:
      continue
  return option_types

def get_brand_attribute(fullskuid):
  """Get the brand attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # now check product_attributes table
  q = DB.fetch_one("""
    SELECT attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name = 'brand'
    AND attribute_value != 'na'
  """, (fullskuid,))
  return q.get('attribute_value')

def get_color_attribute(fullskuid):
  """Get the color attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # now check product_attributes table
  q = DB.fetch_one("""
    SELECT attribute_name, attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name LIKE 'color%%'
    AND (attribute_value != 'na' AND attribute_value != '')
    ORDER BY FIELD(attribute_name, 'colorusa', 'colormap')
    LIMIT 1
  """, (fullskuid,))
  return q.get('attribute_value')


def get_optioned_color(variant):
  """Get the color for a product with options

  Args:
    variant (dict): The variant object

  Returns:
    str: The color
  """

  color = ""
  option_types = translate_option_types(variant)
  if option_types.get('color'):
    color = option_types.get('color')

  attr_color = get_color_attribute(variant.get('fullsku'))
  if attr_color:
    color = attr_color

  return color

def get_size_attribute(fullskuid):
  """Get the size attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # check product attrs, favoring 'sizeusa' attr first
  q = DB.fetch_one("""
    SELECT attribute_name, attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name LIKE '%%size%%'
    AND attribute_value != 'na'
    ORDER BY FIELD(attribute_name, 'sizeusa', 'apparelsize', 'shoesize', 'ring size', 'decorative pillow size', 'bedding size', 'size', 'size2')
    LIMIT 1
  """, (fullskuid,))
  return q.get('attribute_value')


def get_optioned_size(variant):
  """Get the size for a product with options

  Args:
    variant (dict): The variant object

  Returns:
    str: The size
  """

  size = ""
  option_types = translate_option_types(variant)
  if option_types.get('size'):
    size = option_types.get('size')

  attr_size = get_size_attribute(variant.get('fullsku'))
  if attr_size:
    size = attr_size

  return size

def get_material_attribute(fullskuid):
  """Get the material attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # now check product_attributes table
  q = DB.fetch_one("""
    SELECT attribute_name, attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name LIKE 'material%%'
    AND (attribute_value != 'na' AND attribute_value != '')
    ORDER BY FIELD(attribute_name, 'material', 'material features')
    LIMIT 1
  """, (fullskuid,))
  return q.get('attribute_value')


def get_optioned_material(variant):
  """Get the material for a product with options

  Args:
    variant (dict): The variant object

  Returns:
    str: The material
  """

  material = None
  option_types = translate_option_types(variant)
  if option_types.get('material'):
    material = option_types.get('material')

  attr_material = get_material_attribute(variant.get('fullsku'))
  if attr_material:
    material = attr_material

  return material

def get_pattern_attribute(fullskuid):
  """Get the pattern attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # now check product_attributes table
  q = DB.fetch_one("""
    SELECT attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name LIKE '%%pattern%%'
    AND attribute_value != 'na'
  """, (fullskuid,))
  return q.get('attribute_value')


def get_optioned_pattern(variant):
  """Get the pattern for a product with options

  Args:
    variant (dict): The variant object

  Returns:
    str: The pattern
  """

  pattern = None
  option_types = translate_option_types(variant)
  if option_types.get('pattern'):
    pattern = option_types.get('pattern')

  attr_pattern = get_pattern_attribute(variant.get('fullsku'))
  if attr_pattern:
    pattern = attr_pattern

  return pattern

def get_gender_attribute(fullskuid):
  """Get the gender attribute for a given sku

  Args:
    fullskuid (str): The full skuid
  """

  # now check product_attributes table
  q = DB.fetch_one("""
    SELECT attribute_value
    FROM product_attributes
    WHERE fullskuid = %s
    AND attribute_name LIKE '%%gender%%'
    AND attribute_value != 'na'
  """, (fullskuid,))
  return q.get('attribute_value') if q.get('attribute_value') else 'unisex'


def get_optioned_gender(variant):
  """Get the gender for a product with options

  Args:
    variant (dict): The variant object

  Returns:
    str: The gender
  """

  gender = None
  option_types = translate_option_types(variant)
  if option_types.get('suggestedGender'):
    gender = option_types.get('suggestedGender')

  attr_gender = get_gender_attribute(variant.get('fullsku'))
  if attr_gender:
    gender = attr_gender

  if not gender.strip():
    gender = "unisex"
  return gender

def create_optiond_product_link(product, variant):
  """Create a google product object for a product with options

  Args:
    product (Product): The product object
    variant (dict): The variant object

  Returns:
    str: The product link with options as parameters (will be auto-selected on page load)
  """
  product_link = product.get("url")

  op_params = []
  for i, code in enumerate(variant.get('code_list')):
    op_params.append(f"OP{i+1}={code}")

  op_str = "&".join(op_params)

  if '?' in product_link:
    product_link = product_link + "&" + op_str
  else:
    product_link = product_link + "?" + op_str

  return current_app.config["STORE_URL"] + product_link

def create_optioned_title(product_title, option_descs):
  """
  Create a title for a product with options
  remove the vague "T-Shirt or Sweatshirt" from the title
  also "DVD & Blu-ray"
  wherever it occurs.  that is covered in the options

  Args:
    product_title (str): The base product title
    option_descs (list): The option descriptions

  Returns:
    str: The formatted title with options descriptions

  """
  if not option_descs:
    option_descs = []
  newtitle = product_title.replace(' T-Shirt or Sweatshirt', '')
  newtitle = product_title.replace(' DVD & Blu-ray', '')
  newtitle += ' - ' + " - ".join(option_descs)
  return newtitle

def get_option_origprice(product, variant):
  """Get the origprice for a product with options

  Args:
    product (Product): The product object
    variant (dict): The variant object

  Returns:
    float: The origprice as a float

  """

  origprice = get_origprice(product)

  if origprice: # denotes the product is on sale.
    pricechange = sum(float(p) for p in variant.get('pricechanges', []))
    origprice_pricechange = sum(float(p) for p in variant.get('origprice_pricechanges', []))
    if origprice_pricechange > pricechange:
      origprice += origprice_pricechange
    else:
      origprice += pricechange

  return origprice


def create_optioned_products(product):
  """Create a list of google product objects for a base product with options.
  For each variant it will create a base google product, then override certain
  properties with variant-specific values.  Like "Snoopy T-Shirt" becomes
  "Snoopy T-Shirt - Red - Large"

  in the variant object:
  fullsku is the full skuid w/o dashes ex: HBC123SBR
  fullskuid is the full skuid w/ dashes ex: HBC123-S-BR

  Args:
    product (Product): The base product object
  """

  variant_products = []

  for variant in product.get('variant_map', []):
    if variant.get('nla'):
      continue

    skuid = variant.get('fullskuid')
    option_types = translate_option_types(variant)
    origprice = get_option_origprice(product, variant)
    image = variant.get('images', {}).get('large', '').replace('cdn-cgi/image/quality=65,format=auto/', '')
    thumb_image = image.replace('/large/', '/small/')
    descs = variant.get("descriptions", [])
    base_product = create_base_product(product)

    brand = get_brand_attribute(variant.get("fullsku"))
    preorder_date = None
    backorder_date = None
    if variant.get("backorder"):
      if product.get('preorder'):
        preorder_date = format_availability_date(reformat_datestring(variant.get("backorder")))
      else:
        backorder_date = format_availability_date(reformat_datestring(variant.get("backorder")))

    expeditable = get_metadata_value("expeditable", variant.get("fullsku"))

    mfr_min_price = float(get_metadata_value("mfr_min_price", skuid, 0.00))

    additional_shipping = float(get_metadata_value("addl_shipping", variant.get("fullsku"), 0.00))

    ships_free = get_metadata_value("ships_free", variant.get("fullsku"))

    prop65_message = convert_to_ascii(CartItem.get_prop65_message(variant.get("fullsku"))).strip()

    min_bo_price = 0.00
    try:
      min_bo_price = float(get_metadata_value("min_bo_price", variant.get("fullsku"), 0.00))
    except ValueError:
      min_bo_price = 0.00

    macsid = get_invdata_value("macsid", variant.get("fullsku"))

    macs_name = get_invdata_value("name", variant.get("fullsku"))

    inventory_status_code = get_invdata_value("invcode", variant.get("fullsku"))

    inventory_count = get_invdata_value("count", variant.get("fullsku"))

    brand_flag = get_invdata_value("brandflag", variant.get("fullsku"))

    street_date = get_invdata_value("street_date", variant.get("fullsku"))

    release_date = get_invdata_value("release_date", variant.get("fullsku"))

    gender = get_optioned_gender(variant)
    if gender == 'unisex':
      base_gender = base_product.get('gender')
      if base_gender:
        gender = base_gender

    age_group = get_age_group(product, variant.get("fullsku"))

    optioned_product = OrderedDict()
    optioned_product['skuid'] = variant.get('fullskuid')
    optioned_product['parentSkuid'] = product.get('skuid')
    optioned_product["price"] = float(variant.get("price"))
    optioned_product["originalPrice"] = origprice if origprice and origprice > float(variant.get("price")) else None
    optioned_product["itemName"] = create_optioned_title(product.get('name'), variant.get('descriptions'))
    optioned_product["itemUrl"] = create_optiond_product_link(product, variant)
    optioned_product["imageUrl"] = image if image else base_product.get("imageUrl")
    optioned_product["imageUrl"] = thumb_image if thumb_image else base_product.get("thumbUrl")
    optioned_product["checkoutLink"] = current_app.config["STORE_URL"] + f'/checkout?PRODUCT_{skuid}=1'
    optioned_product["availability"] = availability_translate(variant.get("schema_code"))
    optioned_product["schemaAvailability"] = variant.get("schema_code")
    optioned_product["preorderDate"] = preorder_date
    optioned_product["backorderDate"] = backorder_date
    optioned_product["size"] = get_optioned_size(variant)
    optioned_product["color"] = get_optioned_color(variant)
    optioned_product["material"] = get_optioned_material(variant)
    optioned_product["pattern"] = get_optioned_pattern(variant)
    optioned_product["gender"] = gender
    optioned_product["ageGroup"] = age_group
    optioned_product["gtin"] = get_gtin(variant.get("fullsku"))
    optioned_product["mpn"] = variant.get("fullsku")
    optioned_product['isDiscontinued'] = True if get_invdata_value('dicontinuesflag', variant.get("fullsku")) else False
    optioned_product["shippingOverride"] = get_shipping_override(variant.get("price"), product.get("shipping"))
    optioned_product["brand"] = brand if brand else base_product.get("brand")
    optioned_product["isExpressable"] = True if expeditable else False
    optioned_product["mfrMinPrice"] = mfr_min_price or product.get('map')
    optioned_product["additionalShipping"] = round(additional_shipping, 2) if additional_shipping else None
    optioned_product["shipsFree"] = True if ships_free and ships_free == 'Y' else False
    optioned_product["prop65Message"] = prop65_message
    optioned_product["minBackorderPrice"] = round(min_bo_price, 2) if min_bo_price else None
    optioned_product["macsId"] = int(macsid) if macsid and is_number(macsid) else None
    optioned_product["macsName"] = macs_name
    optioned_product["inventoryStatusCode"] = inventory_status_code
    optioned_product['inventoryCount'] = int(inventory_count) if inventory_count and is_number(inventory_count) else None
    optioned_product['brandFlag'] = brand_flag
    optioned_product['streetDate'] = street_date if street_date and street_date != '0000-00-00' else None
    optioned_product['releaseDate'] = release_date if release_date and release_date != '0000-00-00' else None
    optioned_product["attributes"] = get_attributes(variant.get("fullsku"))

    variant_products.append(optioned_product)

  return variant_products

def create_base_product(product):
  """Create a dictionary object for a product with google schema keys

  Args:
    product (Product): The product object

  Returns:
    dict: A product dictionary with google schema keys
  """
  skuid = product.get("skuid")
  gallery = product.get("images", {}).get("gallery", {})
  price = float(product.get("price"))
  origprice = get_origprice(product)
  today = datetime.today().date()
  ninety_days_ago = today - timedelta(days=90)

  availability = None
  if not product.get('options'):
    availability = availability_translate(product.get("availability", {}).get("schema_code"))

  preorder_date = None
  backorder_date = None
  if product.get("backorder"):
    if product.get("preorder"):
      preorder_date = format_availability_date(reformat_datestring(product.get("backorder")))
    else:
      backorder_date = format_availability_date(reformat_datestring(product.get("backorder")))

  color = product.get("color")
  attr_color = get_color_attribute(skuid)
  if attr_color:
    color = attr_color

  size = product.get("size")
  attr_size = get_size_attribute(skuid)
  if attr_size:
    size = attr_size

  material = product.get("material")
  attr_material = get_material_attribute(skuid)
  if attr_material:
    material = attr_material

  pattern = product.get("pattern")
  attr_pattern = get_pattern_attribute(skuid)
  if attr_pattern:
    pattern = attr_pattern

  gender = product.get("gender")
  attr_gender = get_gender_attribute(skuid)
  if attr_gender and attr_gender != 'unisex':
    gender = attr_gender
  else:
    gender = "unisex"
    if any("Women" in c.get('breadcrumb') for c in product.get("breadcrumb", [])):
      gender = "female"
    if any("Men" in c.get('breadcrumb') for c in product.get("breadcrumb", [])):
      gender = "male"
    if 'women' in product.get('name', '').lower():
      gender = "female"
    if 'Men' in product.get('name', ''):
      gender = "male"


  brand = None
  attr_brand = get_brand_attribute(skuid)
  if attr_brand:
    brand = attr_brand
  else:
    brand = get_vendor(product.get("skuid"))

  has_options = True if product.get("options") else False

  expeditable = get_metadata_value("expeditable", skuid)

  mfr_min_price = float(get_metadata_value("mfr_min_price", skuid, 0.00))

  additional_shipping = float(get_metadata_value("addl_shipping", skuid, 0.00))

  ships_free = get_metadata_value("ships_free", skuid)

  prop65_message = convert_to_ascii(CartItem.get_prop65_message(skuid)).strip()

  min_bo_price = 0.00
  try:
    min_bo_price = float(get_metadata_value("min_bo_price", skuid, 0.00))
  except ValueError:
    min_bo_price = 0.00

  macsid = get_invdata_value("macsid", skuid)

  macs_name = get_invdata_value("name", skuid)

  inventory_status_code = get_invdata_value("invcode", skuid)

  inventory_count = get_invdata_value("count", skuid)

  brand_flag = get_invdata_value("brandflag", skuid)

  street_date = get_invdata_value("street_date", skuid)

  release_date = get_invdata_value("release_date", skuid)

  product_lowest_price = price
  product_highest_price = price
  if product.get('variant_map'):
    lowp = min(product.get('variant_map'), key=lambda x: x['price'])
    if lowp:
      product_lowest_price = lowp.get('price')
    highp = max(product.get('variant_map'), key=lambda x: x['price'])
    if highp:
      product_highest_price = highp.get('price')

  image = get_image_by_index(gallery, 0)

  thumb_image = image.replace('/large/', '/small/')

  base_product = OrderedDict()
  base_product['skuid'] = product.get("skuid").strip()
  base_product['itemName'] = product.get("name").strip()
  base_product['description'] = convert_to_ascii(product.get("description")).strip()
  base_product['price'] = price
  base_product['originalPrice'] = origprice if origprice and origprice > price else None
  base_product['hasPricerange'] = product.get("has_pricerange")
  base_product['pricerangeLow'] = float(product_lowest_price) if product.get("has_pricerange") else None
  base_product['preicerangeHigh'] = float(product_highest_price) if product.get("has_pricerange") else None
  base_product['itemUrl'] = current_app.config["STORE_URL"] + product.get("url")
  base_product['imageUrl'] = image
  base_product['thumbUrl'] = thumb_image
  base_product['additionalImages'] = get_alternate_images(gallery)
  base_product['availability'] = availability
  base_product['schemaAvailability'] = product.get("availability", {}).get("schema_code")
  base_product['preorderDate'] = preorder_date
  base_product['backorderDate'] = preorder_date
  base_product['googleProductCategory'] = product.get("default_category", {}).get("google_category_id")
  base_product['categories'] = get_categories(product)
  base_product['defaultCategory'] = product.get("default_category", {}).get("breadcrumb")
  base_product['brand'] = brand
  base_product['gtin'] = get_gtin(product.get("skuid"))
  base_product['mpn'] = product.get("skuid")
  base_product['ageGroup'] = get_age_group(product, product.get("skuid"))
  base_product['size'] = size
  base_product['color'] = color
  base_product['gender'] = gender
  base_product['material'] = material
  base_product['pattern'] = pattern
  base_product['checkoutLink'] = current_app.config["STORE_URL"] + f'/checkout?PRODUCT_{skuid}=1' if not has_options else None
  base_product['shippingOverride'] = get_shipping_override(product.get("price"), product.get("shipping"))
  base_product['creationDate'] = product.get("creation_date")
  base_product['mfrMinPrice'] = mfr_min_price or product.get('map')
  base_product['maxQuantity'] = product.get("maxq") if product.get("maxq") else None
  base_product['hasOptions'] = has_options
  base_product['h1Tag'] = product.get("h1_tag")
  base_product['metaDescTag'] = product.get("meta_desc_tag")
  base_product['isExclusive'] = True if product.get("exclusive") else False
  base_product['noPaypal'] = True if product.get("no_paypal") else False
  base_product['colorCount'] = product.get("color_count")
  base_product['styleCount'] = product.get("style_count")
  base_product['isPersonalized'] = True if product.get("custom") else False
  base_product['priceBreak'] = product.get("discount_desc")
  base_product['isDiscontinued'] = True if get_invdata_value('dicontinuesflag', skuid) else False
  base_product['isSlapper'] = True if product.get("slapper") else False
  base_product['isFeatureable'] = True if product.get("featureable") else False
  base_product['forceFeedInclusion'] = True if product.get("force_feed_inclusion") else False
  base_product['isNla'] = True if product.get("nla") else False
  base_product['isDropship'] = True if product.get("drop_ship") else False
  base_product['isNew'] = True if product.get('creation_date') >= ninety_days_ago else False
  base_product['dropShipLeadTime'] = product.get("drop_ship_type", {}).get('description') if product.get("drop_ship") else None
  base_product['usShippingOnly'] = True if product.get("us_shipping_only") else False
  base_product['continentalUsOnly'] = True if product.get("restrict_ship") else False
  base_product['productRating'] = round(product.get("pr_rating"), 1) if product.get("pr_rating") else None
  base_product['reviewCount'] = product.get("pr_reviewcount")
  base_product['triggerSuppress'] = True if product.get("trigger_suppress") else False
  base_product['keywords'] = split_to_list(product.get("keywords"))
  base_product['isWaitlist'] = True if product.get("is_waitlist") else False
  base_product['isGiftwrappable'] = True if product.get("giftwrap") else False
  base_product['isExpressable'] = True if expeditable == 'YES' else False
  base_product['calloutText'] = product.get("callout")
  base_product['additionalShipping'] = round(additional_shipping, 2) if additional_shipping else None
  base_product['shipsFree'] = True if ships_free and ships_free == 'Y' else False
  base_product['prop65Message'] = prop65_message
  base_product['minBackorderPrice'] = round(min_bo_price, 2) if min_bo_price > 0 else None
  base_product['inventoryStatusCode'] = inventory_status_code
  base_product['inventoryCount'] = int(inventory_count) if inventory_count and is_number(inventory_count) else None
  base_product['brandFlag'] = brand_flag
  base_product['streetDate'] = street_date if street_date and street_date != '0000-00-00' else None
  base_product['releaseDate'] = release_date if release_date and release_date != '0000-00-00' else None
  base_product['macsId'] = int(macsid) if macsid and is_number(macsid) else None
  base_product['macsName'] = macs_name
  base_product['badges'] = product.get("badges")
  base_product['salesRank'] = get_sales_rank(skuid)
  base_product['additionalDescription'] = convert_to_ascii(product.get("description2")).strip() if product.get("description2") else None
  base_product['variants'] = []
  base_product['attributes'] = get_attributes(skuid)

  return base_product


@current_app.cli.command("create_master_feed")
def create_master_feed():
  print("Creating master feed (feeds/master.py)")

  # get all skuids

  products = []
  q = DB.fetch_all("SELECT SKUID AS skuid FROM products")
  for skuid in q['results']:
    product = Product.from_skuid(skuid['skuid'], True)

    # skip nla products BUT include NLA products specifically marked for feed inclusion
    # or marked as waitlist items
    if not product or not product.get('price') or \
      (product.get("nla") and not product.get("force_feed_inclusion")) or \
      (product.get("nla") and not product.get("is_waitlist")):
      continue

    #pprint(product.to_dict())

    base_product = create_base_product(product)
    if product.has_options():
      base_product['variants'] = create_optioned_products(product)

    products.append(base_product)

  # Specify the path to the JSON file
  store_code = re.sub(r'\d', '', current_app.config["STORE_CODE"])
  tmp_file_path = "public_html/master_feed.json.tmp"
  file_path = f"public_html/{store_code}_master_feed.json"

  # Write the data to the JSON file
  with open(tmp_file_path, 'w') as json_file:
      json.dump(products, json_file, indent=4, cls=CustomJSONEncoder)

  if os.path.exists(tmp_file_path):
    if os.path.exists(file_path):
        os.remove(file_path)  # Remove the existing file
    os.rename(tmp_file_path, file_path)
    print(f"File renamed to {file_path}")

