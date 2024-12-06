""" Flask Application Module

Creates the Flask application using the app factory method
"""

from datetime import datetime
import os
import logging
from flask import Flask, current_app, g, request, session


def register_extensions(app):
    """Registers Flask extensions

    Args:
      app (app): The Flask application
    """
    from .modules.extensions import db, compress, cache, mail, sess, RegexConverter

    compress.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    sess.init_app(app)
    mail.init_app(app)
    app.url_map.converters["regex"] = RegexConverter


def create_app():
    """Creates the Flask application

    Returns:
      app: The Flask application
    """
    app = Flask(__name__, static_folder="assets")
    with app.app_context():
        app.config.from_object("config." + "config." + os.environ["ENV"])
        register_extensions(app)

        # standard application logging
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

        # post critical errors to notification service
        if app.config.get('PRODUCTION'):
          from .modules.http import CustomHTTPErrorHandler
          error_notify_handler = CustomHTTPErrorHandler()
          error_notify_handler.setLevel(logging.ERROR)
          app.logger.addHandler(error_notify_handler)


        # template routes
        from .routes.public.views import (
            home,
            category,
            product,
            search,
            cart,
            partials,
            quickorder,
            other,
            content,
            user,
            order,
            checkout,
            receipt_lookup,
        )

        app.register_blueprint(home.mod)
        app.register_blueprint(category.mod)
        app.register_blueprint(product.mod)
        app.register_blueprint(cart.mod)
        app.register_blueprint(search.mod)
        app.register_blueprint(partials.mod)
        app.register_blueprint(quickorder.mod)
        app.register_blueprint(other.mod)
        app.register_blueprint(content.mod)
        app.register_blueprint(user.mod)
        app.register_blueprint(order.mod)
        app.register_blueprint(checkout.mod)
        app.register_blueprint(receipt_lookup.mod)

        # api routes
        from .routes.public.api import (
            product,
            category,
            cart,
            other,
            privacy,
            contact,
            catalogrequest,
            user,
            subscription,
            checkout,
            order,
            test,
            receipt_lookup,
        )

        app.register_blueprint(user.mod)
        app.register_blueprint(product.mod)
        app.register_blueprint(category.mod)
        app.register_blueprint(cart.mod)
        app.register_blueprint(other.mod)
        app.register_blueprint(subscription.mod)
        app.register_blueprint(privacy.mod)
        app.register_blueprint(contact.mod)
        app.register_blueprint(catalogrequest.mod)
        app.register_blueprint(checkout.mod)
        app.register_blueprint(order.mod)
        app.register_blueprint(test.mod)
        app.register_blueprint(receipt_lookup.mod)

        from .modules.helpers import (
            format_rating,
            rating_list,
            serialize,
            sanitize,
            format_currency,
            abbrev,
            image_path,
            dump_json_as_ascii,
            match_uuid,
            days_seconds
        )
        from .modules.http import (
          page_not_found,
          error_500,
          add_security_headers,
          session_safe_get,
          get_session_id,
        )
        from .modules.category.categories import get_breadcrumb_string
        from .modules.cart import Cart
        from .modules.cart.post_process import post_process_cart
        from .modules.cart.params import set_session_defaults, save_params_to_session, process_params, check_promo_code
        from .modules.preload import get_preload_data, get_flip_catalog
        from .modules.user import create_address_hash, create_phone_hash

        app.register_error_handler(404, page_not_found)
        app.register_error_handler(500, error_500)

        @app.before_request
        def do_before():
            """Procedures to do before normal Flask request processing.  The order is immportant"""

            # security - limit request sizes
            content_length = request.content_length
            max_length = current_app.config["MAX_CONTENT_LENGTH"]
            if content_length and content_length > current_app.config["MAX_CONTENT_LENGTH"]:
              current_app.logger.error(f"Request Entity Too Large: {content_length} > {current_app.config['MAX_CONTENT_LENGTH']}")
              return "Request Entity Too Large", 413


            # create global messages that need to be available across the front end
            g.messages = {"errors": [], "success": [], "promo": "", "added": [], "updated": [], "removed": [], "notes": []}

            # load cached promotion data into a global
            g.cached = get_preload_data()

            # set default session variables (if not already set)
            set_session_defaults()

            #  save query params and form data as session vars by default (mimics hazel)
            save_params_to_session()

            # check if any entered code (coupon or source) matches a promotion, set to global if so
            g.promo_code = check_promo_code()

            # load cart into global object
            cart_id = None
            cart_tmp = request.cookies.get(current_app.config["CART_COOKIE_NAME"])
            if cart_tmp and match_uuid(cart_tmp):
                cart_id = cart_tmp
            cart_json = Cart.load_cart_from_redis(cart_id)
            g.cart = Cart.from_json(cart_json)  # is an empty cart model if no cart_json

            # look for "special" params in request.form or request.args (like cart adds)
            # these params can trigger adds/removes from ANY url
            process_params()

            # perform procedures that depend on the cart (and its items) being fully known
            # for example, group discounts
            if not g.cart.is_empty():
                post_process_cart()

        @app.after_request
        def do_after(response):
            """Procedures to do after normal Flask request processing but before respose sent to user.  The order is immportant"""

            # persist cart to redis if it has items, set id to cookie
            response = Cart.persist_cart(response)

            # these cookies are requested bv cro-metrics for catalog recipient attribution
            # response = set_hash_cookies(response)
            expires = 62208000 # 2 years
            address_hash = create_address_hash()
            if address_hash:
              response.set_cookie(
                  'a_h_id',
                  address_hash,
                  max_age=expires,
                  secure=True,
                  samesite="Lax",
              )
            phone_hash = create_phone_hash()
            if phone_hash:
              response.set_cookie(
                  'p_h_id',
                  phone_hash,
                  max_age=expires,
                  secure=True,
                  samesite="Lax",
              )

            # if this is failover, set a cookie which will keep the customer there for the session
            # the cookie itself is poorly named, it's not just for testing
            if current_app.config.get("FAILOVER") and request.path not in ["/forgetme"]:
                response.set_cookie("cloudflare_test_failover", "failover")

            # add security headers to response
            return add_security_headers(response)

        @app.context_processor
        def template_utils():
            """Makes functions available inside templates"""
            from .modules.category.categories import (
                get_category,
                get_subcategories,
                get_all_category_menu,
                get_desktop_nav,
                get_mobile_nav,
                get_mobile_heading_nav,
            )
            from .modules.helpers import (
                get_alphabet,
                get_months,
                get_random_string,
                split_to_list,
                image_size,
                strip_html,
                double_encode,
                is_int,
                replace_double_quote,
                md5_encode,
                get_order_notes,
                is_cs_open,
                is_valid_isbn
            )
            from .modules.product.personalization import get_lakes, get_personalization_prompts
            from .modules.regions import get_states, get_countries
            from .modules.banners import get_heading_banners, get_catalog_image
            from .modules.http import get_cart_id, has_noindex, get_canonical_override
            from .modules.preload import get_search_state


            return dict(
                get_category=get_category,
                get_subcategories=get_subcategories,
                get_all_category_menu=get_all_category_menu,
                abbrev=abbrev,
                rating_list=rating_list,
                get_breadcrumb_string=get_breadcrumb_string,
                get_lakes=get_lakes,
                get_alphabet=get_alphabet,
                sanitize=sanitize,
                session_safe_get=session_safe_get,
                str=str,
                int=int,
                is_int=is_int,
                get_months=get_months,
                datetime=datetime,
                get_desktop_nav=get_desktop_nav,
                get_mobile_nav=get_mobile_nav,
                get_random_string=get_random_string,
                get_mobile_heading_nav=get_mobile_heading_nav,
                image_path=image_path,
                get_states=get_states,
                get_countries=get_countries,
                get_session_id=get_session_id,
                split_to_list=split_to_list,
                get_heading_banners=get_heading_banners,
                image_size=image_size,
                get_cart_id=get_cart_id,
                get_flip_catalog=get_flip_catalog,
                has_noindex=has_noindex,
                get_canonical_override=get_canonical_override,
                strip_html=strip_html,
                get_personalization_prompts=get_personalization_prompts,
                double_encode=double_encode,
                replace_double_quote=replace_double_quote,
                get_catalog_image=get_catalog_image,
                md5_encode=md5_encode,
                get_order_notes=get_order_notes,
                is_cs_open=is_cs_open,
                is_valid_isbn=is_valid_isbn,
                get_search_state=get_search_state,
                create_address_hash=create_address_hash,
                create_phone_hash=create_phone_hash
            )

        # custom template filters
        app.jinja_env.filters["serialize"] = serialize
        app.jinja_env.filters["sanitize"] = sanitize
        app.jinja_env.filters["format_rating"] = format_rating
        app.jinja_env.filters["format_currency"] = format_currency
        app.jinja_env.filters["dump_json_as_ascii"] = dump_json_as_ascii

        # flask-cli commands
        from .commands.redis import clear_cache, clear_sessions, clear_carts, expire_carts
        from .commands.db_test import test1
        from .commands.feeds.master import create_master_feed
        from .commands.feeds.survey import update_survey

    return app
