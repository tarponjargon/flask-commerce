from flask import g, session, current_app

def apply_club_discount():
    for item in g.cart.get_items():
      if item.get("bleuprice"):
        continue
      product = item.get("product", {})
      if product.get("bbsdiscount", 0.00) and \
        product.get("bbsdiscount") < product.get("price"):
          item.set("price", float(product.get("bbsdiscount")))
          product.set("bleuorigprice", float(product.get("price")))
          product.set("bleuprice", True)
          if product.get("origprice", 0.00) and product.get("origprice", 0.00) > product.get("price"):
            product.set("origprice", float(product.get("origprice")))
          if product.get("ppd1_price", 0.00) and product.get("ppd1_price", 0.00) > product.get("price"):
            product.set("ppd1_price", float(product.get("ppd1_price")))
          item.set("bleuprice", True)
          current_app.logger.debug("club discount {}".format(product.get("bbsdiscount")))
