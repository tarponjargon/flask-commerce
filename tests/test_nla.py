def test_nla(app):
    """Test NLA items"""
    with app.test_request_context():
        from flask import g
        from flask_app.modules.extensions import DB
        from flask_app.modules.product import Product
        from flask_app.modules.cart_item import CartItem

        app.preprocess_request()

        results = DB.fetch_all("SELECT SKUID as skuid FROM products WHERE INVENTORY = 1 LIMIT 100")["results"]
        for res in results:
            skuid = res["skuid"]
            print("Testing NLA item " + skuid)
            product = Product.from_skuid(res["skuid"])

            # test product object can be created
            assert isinstance(product, Product)
            assert product.get("skuid") == res["skuid"]
            assert product.get("nla") == 1

            # test that cart_item is none
            cart_item = CartItem.from_dict({"skuid": product.get("skuid")})
            assert cart_item == None
            assert f"Product {skuid} is not available." in g.messages["errors"]
