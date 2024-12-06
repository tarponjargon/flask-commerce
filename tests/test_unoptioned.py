def test_unoptioned(app):
    """Test regular, unoptioned items (i.e. no variants)"""
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
              AND (products.OPTIONS IS NULL OR products.OPTIONS = '')
              AND invdata.is_waitlist != 1
              LIMIT 100
            """
        )["results"]
        for res in results:
            skuid = res["skuid"]
            product = Product.from_skuid(res["skuid"])

            print("Testing unoptioned item " + skuid)

            # test product object can be created
            assert isinstance(product, Product)
            assert product.get("skuid") == skuid

            # test cart item can be created
            cart_item = CartItem.from_dict({"skuid": product.get("skuid")})
            assert isinstance(cart_item.get_item(), dict)
            assert cart_item.get("price")

            # test it can be  added to cart
            cart = Cart.from_json(None)
            cart.add_item(cart_item)
            assert cart.get_item_by_skuid(skuid)
            last_added = cart.get_last_added()
            assert last_added.get("skuid") == skuid
