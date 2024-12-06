import random


def test_optioned(app):
    """Test optioned items (i.e. items with variants)"""
    with app.test_request_context():
        from flask_app.modules.extensions import DB
        from flask_app.modules.product import Product
        from flask_app.modules.cart import Cart
        from flask_app.modules.cart_item import CartItem

        app.preprocess_request()
        results = DB.fetch_all(
            f"""
              SELECT
                products.SKUID as skuid
              FROM products
              LEFT JOIN invdata ON products.SKUID = invdata.skuid
              WHERE products.INVENTORY != 1
              AND (products.CUSTOM IS NULL OR products.CUSTOM = '')
              AND (products.OPTIONS IS NOT NULL AND products.OPTIONS != '')
              AND invdata.is_waitlist != 1
            """
        )["results"]
        for res in results:
            skuid = res["skuid"]

            # unfortunately there are a couple more ways optioned items can be NLA.  skip if true
            q = DB.fetch_one(
                "SELECT COUNT(*) AS avail FROM options_index WHERE skuid = %(skuid)s AND nla = 0", {"skuid": skuid}
            )
            r = DB.fetch_one(
                "SELECT COUNT(*) AS avail FROM invdata WHERE skuid LIKE %(skuid_wildcard)s AND dicontinuesflag != 1",
                {"skuid_wildcard": skuid + "%"},
            )
            if not q.get("avail") or not r.get("avail"):
                continue

            print("Testing optioned item " + skuid)

            cart = Cart.from_json(None)
            product = Product.from_skuid(res["skuid"])
            vmap = product.get("variant_map")

            # test product object can be created
            assert isinstance(product, Product)
            assert product.get("skuid") == skuid
            assert isinstance(vmap, list)

            # print("Price:")
            # print(product.get("price"))

            # add item to the cart w/o options and test that the 'missing variants' methods
            item = {"skuid": product.get("skuid"), "quantity": 2}
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_variants() == True
            cart.add_item(cart_item)
            assert isinstance(cart.has_missing_variants(), CartItem)

            # remove the item, test it's gome
            cart.remove_item(skuid)
            assert not cart.get_item_by_skuid(skuid)

            # select a the first "legal" set of codes to submit as simulated option selections and add that
            legalset = next((p for p in vmap if p.get("nla") == 0), None)
            item["variant_codes"] = legalset.get("code_list")
            fullskuid = skuid + "-" + "-".join(item["variant_codes"])
            cart_item = CartItem.from_dict(item)
            cart.add_item(cart_item)

            print("Fully optioned item " + fullskuid)

            # test it's in the cart and it's set as last_added
            assert cart.get_item_by_skuid(fullskuid)
            last_added = cart.get_last_added()
            assert last_added.get("skuid") == fullskuid

            # test the subtotal calc.
            # the x2 is b/c we changed the qty to 2 earlier
            # commented out 2/16/24 as the 2nd caparison value doesn't take into account if the item is on sale like thru weekly_specials
            # fullsku = cart_item.get('skuid').replace('-', '')
            # o = DB.fetch_one(
            #     "SELECT price FROM options_index WHERE fullsku = %(fullsku)s", {"fullsku": fullsku}
            # )
            # assert round(cart_item.get_total_price(), 2) == round(float(o.get("price") * 2), 2)

            # test there's only 1 item in the cart
            assert len(cart.get_items()) == 1

            # test the missing variants methods
            assert cart_item.is_missing_variants() == False
            assert not cart.has_missing_variants()
