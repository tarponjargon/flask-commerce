from copy import deepcopy
from flask import g


def test_cart_persist(app):
    """Test that the cart persists to redis"""
    with app.test_request_context():
        from flask_app.modules.extensions import DB, redis_cart
        from flask_app.modules.product import Product
        from flask_app.modules.cart import Cart
        from flask_app.modules.helpers import match_uuid
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
              LIMIT 1
            """
        )["results"]
        for res in results:
            g.cart = Cart.from_json(None)
            product = Product.from_skuid(res["skuid"])
            personalization = product.get("personalization")

            # populate personalization values (an array of arrays)
            item = {"skuid": product.get("skuid"), "quantity": 2, "personalization": []}
            for i in range(0, item["quantity"]):
                pslice = []
                for pers in personalization:
                    prompt = deepcopy(pers)
                    maxlength = int(prompt.get("maxlength", 2))
                    prompt["value"] = get_random_string(maxlength)
                    pslice.append(prompt)
                item["personalization"].append(pslice)

            # create cart item and add it to the cart
            cart_item = CartItem.from_dict(item)
            g.cart.add_item(cart_item)

            # persist the cart and test UUID returned
            cart_id = g.cart.save_cart(None)
            assert match_uuid(cart_id)

            # delete cart object
            g.cart = None

            # retrieve cart from redis and instantiate it
            cart_json = redis_cart.get(cart_id)
            g.cart = Cart.from_json(cart_json)

            # check that the current item is in reloaded cart
            recovered_item = g.cart.get_item_by_skuid(res["skuid"])
            assert isinstance(recovered_item, CartItem)

            # check that the current item pers length is same in recovered cart
            assert len(item.get("personalization")) == len(recovered_item.get("personalization"))

            # delete the persisted cart and test it's gone
            redis_cart.delete(cart_id)

            assert not redis_cart.get(cart_id)
