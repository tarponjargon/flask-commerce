""" Scripts for manipulating the redis store(s) """

from datetime import datetime, timedelta
import json
from flask import current_app
from flask_app.modules.extensions import redis_cart
from flask_app.modules.helpers import do_cache_clear


@current_app.cli.command("clear_cache")
def clear_cache():
    """clears the cached/memoized objects in redis db"""
    do_cache_clear()


@current_app.cli.command("clear_sessions")
def clear_sessions():
    """clears all flask sessions (stored in redis db)"""
    current_app.config["SESSION_REDIS"].flushdb()


@current_app.cli.command("clear_carts")
def clear_carts():
    """clears all carts (stored in redis db)"""
    redis_cart.flushdb()


@current_app.cli.command("expire_carts")
def expire_carts():
    """deletes old carts comparing a timestamp of x days ago and timestamp stored in cart object (stored in redis db2)"""
    max_age = datetime.now() - timedelta(days=current_app.config["CART_MAX_AGE"])
    max_age_int = int(max_age.strftime("%Y%m%d%H%M%S"))
    for key in redis_cart.scan_iter("*"):
        json_cart = redis_cart.get(key)
        if json_cart:
            cart = {}
            try:
                cart = json.loads(json_cart)
            except ValueError:
                current_app.logger.error("session cart JSON decoding failed")

            if cart and cart.get("timestamp"):
                print("timestamp", cart.get("timestamp"))
                ts_int = int(cart.get("timestamp"))
                if ts_int < max_age_int:
                    print("EXPIRED cart", key)
                    redis_cart.delete(key)
                else:
                    print("NOT EXPIRED cart", key)
