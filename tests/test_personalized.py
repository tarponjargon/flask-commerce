from copy import deepcopy


def test_personalized(app):
    """Test optioned items (i.e. items with variants)"""
    with app.test_request_context():
        from flask_app.modules.extensions import DB
        from flask_app.modules.product import Product
        from flask_app.modules.cart import Cart
        from flask_app.modules.cart_item import CartItem
        from flask_app.modules.helpers import get_random_string

        app.preprocess_request()
        results = DB.fetch_all(
            f"""
              SELECT
                products.SKUID as skuid
              FROM products
              WHERE INVENTORY != 1
              AND (OPTIONS IS NULL OR OPTIONS = '')
              AND (CUSTOM IS NOT NULL AND CUSTOM != '')
            """
        )["results"]
        for res in results:
            skuid = res["skuid"]

            print("Testing personalized item " + skuid)

            cart = Cart.from_json(None)
            product = Product.from_skuid(res["skuid"])
            personalization = product.get("personalization")

            # test product object can be created
            assert isinstance(product, Product)
            assert product.get("skuid") == skuid
            assert isinstance(personalization, list)

            # add item to the cart w/o personalization and test missing_pers methods
            item = {"skuid": product.get("skuid"), "quantity": 2}
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_pers() == True
            cart.add_item(cart_item)

            # populate personalization values (an array of arrays)
            item["personalization"] = []
            for i in range(0, item["quantity"]):
                pslice = []
                for pers in personalization:
                    prompt = deepcopy(pers)
                    maxlength = int(prompt.get("maxlength", 2))
                    prompt["value"] = get_random_string(maxlength)
                    pslice.append(prompt)
                item["personalization"].append(pslice)

            # re-add item with updated personalization
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_pers() == False
            added = cart.add_item(cart_item)
            assert not cart.has_missing_pers()

            # test there's only 1 item in the cart
            assert len(cart.get_items()) == 1

            # increase qty to 3 and test missing pers methods
            item["quantity"] = 3
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_pers() == True

            # populate the missing value
            item["personalization"].append(deepcopy(personalization))
            for i in range(0, len(item["personalization"][2])):
                maxlength = int(item["personalization"][2][i].get("maxlength", 2))
                item["personalization"][2][i]["value"] = get_random_string(maxlength)

            # resubmit fully-personalized item
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_pers() == False
            added = cart.add_item(cart_item)
            assert not cart.has_missing_pers()

            # remove personalization values
            item["personalization"] = []
            for i in range(0, item["quantity"]):
                pslice = []
                for pers in personalization:
                    prompt = deepcopy(pers)
                    prompt["value"] = ""
                    pslice.append(prompt)
                item["personalization"].append(pslice)

            # resubmit, make sure missing pers methods fail
            cart_item = CartItem.from_dict(item)
            assert cart_item.is_missing_pers() == True
            added = cart.add_item(cart_item)
