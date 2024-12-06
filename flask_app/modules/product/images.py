""" Functions related to a product's images """

import copy
from flask import current_app
from flask_app.modules.extensions import DB, cache
from flask_app.modules.product.variants import get_variants_to_images
from flask_app.modules.helpers import jpg_extension, image_size


@cache.memoize()
def get_images(product=None):
    """Gets all images associated with the base product

    Provides a list of the images themselves, a gallery, and variant associations

    Args:
      product_data (dict): The product data as a dictionary

    Returns:
      dict: A dictionary containing the products base images in root keys, and a
            'gallery' list containing all images (including alternates) with
            any associated variant data
    """
    if product is None or "skuid" not in product or "image" not in product:
        product = {}

    images = {}
    gallery = []

    # make default image the first in the gallery
    gallery.append({"skuid": product["skuid"], "variant_data": {}, "image": jpg_extension(product["image"])})

    # if there's a video, make it the 2nd slot in the gallery
    if (product.get("video_filename") and product.get('video_poster_filename')):
      gallery.append({
        "skuid": product["skuid"],
        "variant_data": {},
        "image": product["video_poster_filename"],
        "video": product["video_filename"]
      })


    # parse out image keys from main product into their own 'images' dict
    image_keys = ["image", "bigimg", "smlimg", "zoom", "image_rect"]
    # this adds keys for 'altimg1' thru 'altimg32'
    image_keys.extend([f"altimg{i}" for i in range(1, current_app.config["MAX_ALT_IMAGES"] + 1)])
    for f in image_keys:
        if f in product and product[f] and product[f].strip() != "":
            filename = jpg_extension(product[f])
            if f.startswith("altimg"):
                gallery.append(
                    {
                        "skuid": product["skuid"],
                        "variant_data": [],
                        "image": filename,
                    }
                )
            else:
                images[f] = filename

    # make sure 'zoom', 'smlimg' and 'bigimg' have defaults
    images["smlimg"] = images["smlimg"] if images.get("smlimg") else images.get("image")
    images["bigimg"] = images["bigimg"] if images.get("bigimg") else images.get("image")
    images["zoom"] = images["bigimg"] if images.get("bigimg") else images.get("image")

    # merge in variant data to any gallery images that are variant illustrations
    if "variants_to_images" in product and product["variants_to_images"]:
        gc = copy.deepcopy(gallery)
        for o in product["variants_to_images"]:
            x = next(
                (i for (i, d) in enumerate(gc) if d["image"] == o["image"]),
                -1,
            )
            if x > -1:
              gallery[x]["variant_data"] = o["variant_data"]
            else:
              gallery.append(o)

    images["gallery"] = gallery
    return images


@cache.memoize()
def get_image_by_fullskuid(fullskuid):
    """Gets an image path given a full skuid.  Will return a variant-specific image if one exists

    I'm using image_size function return value (tuple len =2 ) as a proxy to tell if an image exists on the filesystem

    Args:
      fullskuid (str): The full skuid (with dashes) or base skuid if no variants

    Returns:
      str: The relative path to the image file
    """
    if not fullskuid:
        return ""

    sku_parts = fullskuid.split("-")

    if not len(sku_parts):
        return ""

    image_path = ""
    tmp_path = ""
    image_sz = ["", ""]
    base_skuid = sku_parts[0]
    image_dir = "/graphics/products/small/"

    # if the sku is optioned, try to get a variant-level image
    if len(sku_parts) > 1:
        varmap = get_variants_to_images(base_skuid)
        if varmap and len(varmap) > 0:
            progressive_sku = ""
            for part in sku_parts:
                progressive_sku += part
                imageobj = next((i for i in varmap if i["fullskuid"] == progressive_sku), None)
                if imageobj and "image" in imageobj and imageobj["image"]:
                    tmp_path = image_dir + jpg_extension(imageobj["image"])
                    image_sz = image_size(tmp_path)
                    if image_sz[0]:
                        image_path = tmp_path
                    break

    # if an image path is found, no need to go further
    if image_path:
        return image_path

    # try using the sku itself
    tmp_path = image_dir + jpg_extension(base_skuid)
    image_sz = image_size(tmp_path)
    if image_sz[0]:
        image_path = tmp_path

    # see if the item is in products and the image can be loaded from that record's data
    res = DB.fetch_one(
        """
      SELECT IMAGE from products
      WHERE SKUID = %(base_skuid)s
    """,
        {"base_skuid": base_skuid},
    )

    if res.get("IMAGE"):
        tmp_path = image_dir + jpg_extension(res.get("IMAGE"))
        image_sz = image_size(tmp_path)

    if image_sz[0]:
        image_path = tmp_path
        return image_path

    # i'm going to return the latest tmp path because it's possible the image is loaded remotely
    return tmp_path
