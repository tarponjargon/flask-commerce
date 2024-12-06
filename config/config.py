from datetime import timedelta
import redis
import os


class Config(object):
    """config vars common to all Flask app environments"""

    STORE_EMAIL = os.environ.get('STORE_EMAIL')
    STORE_CS_EMAIL = os.environ.get('STORE_EMAIL')
    STORE_CODE = os.environ.get("STORE_CODE")
    STORE_NAME = "FlaskCommerce"
    STORE_ADDRESS1 = "1234 Test St."
    STORE_CITY = "Springfield"
    STORE_STATE = "MA"
    STORE_ZIP = "01101"
    STORE_PHONE = "800-123-4567"
    STORE_PHONE_MOBILE = "800-123-4567"
    STORE_CUSTOMER_SERVICE = "800-123-4567"
    STORE_CUSTOMER_SERVICE_PHONE = "800-123-4567"
    STORE_CUSTOMER_SERVICE_HOURS = "(9 a.m. to 7 p.m. ET, Monday through Friday)"
    STORE_CS_HOUR_OPEN = 9
    STORE_CS_HOUR_CLOSE = 19
    STORE_TAGLINE = (
        "Uniquely Thoughtful Gifts for All Ages and Occasions at FlaskCommerce Catalog"
    )
    STORE_META_DESCRIPTION = "FlaskCommerce is your online catalog of uniquely thoughtful personalized gifts, clothing, jewelry, accessories, home décor, and more gifts for all ages and occasions!"
    STORE_LOGO = "/assets/images/logo.svg"
    STORE_FAVICON = "/favicon.ico"
    STORE_ACCESSIBILITY_CONTACT = os.environ.get('STORE_EMAIL')
    STORE_ADMIN = os.environ.get('STORE_EMAIL')
    ERROR_NOTIFY_URL = os.environ.get("ERROR_NOTIFY_URL")
    ERROR_NOTIFY_AUTH = os.environ.get("ERROR_NOTIFY_AUTH")
    ORDER_PREFIX = "H"
    AK_HI_SURCHARGE = 10.00
    OVERNIGHT_AK_HI: 45.00
    DIVISION = "04"
    DEFAULT_EMAIL_SOURCE = "S_DEFAULT1"
    MAX_CONTENT_LENGTH = 2097152  # 2MB
    EXPIREABLE_COUPON_PREFIX = "XZR"

    # store defaults
    CLUB_SKUS = []
    SHIPPING_COUNTRIES = ["USA"]
    LINEITEM_LIMIT = 90
    DEFAULT_MAXQ = 25
    DEFAULT_IMAGE = "/assets/images/default_image.png"
    GTM_ID = os.environ.get("GTM_ID")
    SITE_CODE = "flaskcommerce"
    IMAGE_BASE = ""
    PRODUCT_IMAGE_PATH = "/graphics/products"
    MAX_ALT_IMAGES = 32
    PRODUCTS_PER_PAGE = (
        24  # only used for default productlisting which is generally not active
    )
    ROOT_CATEGORY = "root"
    CATEGORY_MAX_DEPTH = 5
    ABBREV_LENGTH = 240
    DEFAULT_COUPON = "EMSYAY"
    DEFAULT_GIFTWRAP = "AW5492"
    CLUB_GIFTWRAP = "AW5492"
    PDP_IMAGE_DIR = (
        "regular"  # specifies what directory to load the default product image out of
    )
    ZOOM_DIR = "zoom"  # specifies what directory to load the product zoom image out of
    # these fields cannot be set to the session by request params, only from the server side
    FORBIDDEN_FIELDS = [
        "customer_id",
        "cart",
        "credit_code_saved",
        "credit_security_code_saved",
        "order_id",
        "order_temp",
        "referrer",
        "BBSVALIDATED",
        "wpp_txn_id",
        "wpp_token",
        "wpp_payerid",
        "wpp_correlationid",
        "nontaxable_items",
    ]
    SESSION_DEFAULTS = {"ship_method": "24", "payment_method": "standard"}
    NLA_CODES = ["C1", "C2", "C4", "KC"]
    EMPLOYEE_DISCOUNTS = [
        {
            "code": "EMPHUD",
            "location": "Widget Main Office",
            "address": {
                "ship_street": "FlaskCommerce HQ",
                "ship_street2": "1234 Test St",
                "ship_city": "Springfield",
                "ship_state": "MA",
                "ship_postal_code": "01101",
                "ship_contry": "USA",
            },
        }
        {"code": "EMPSHIP", "location": "Employee Residence", "address": None},
    ]

    # db conns
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_AUTOCOMMIT = True
    MYSQL_LOG_QUERY = False

    # view/function cache (redis thru flask_caching) uses redis db3
    CACHE_TYPE = "null"
    CACHE_REDIS_HOST = os.environ.get("REDIS_HOST")
    CACHE_REDIS_PORT = os.environ.get("REDIS_PORT")
    CACHE_REDIS_DB = os.environ.get("REDIS_CACHE_DB")
    CACHE_DEFAULT_TIMEOUT = 86400  # 1 day

    # sessions (redis thru flask-session) uses redis db4
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = os.environ.get("STORE_CODE")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(
        f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_SESSION_DB')}"
    )

    # carts (redis thru redis-py) uses redis db5
    CART_COOKIE_NAME = "cart_id"
    CART_REDIS_HOST = os.environ.get("REDIS_HOST")
    CART_REDIS_PORT = os.environ.get("REDIS_PORT")
    CART_REDIS_DB = os.environ.get("REDIS_CART_DB")
    CART_MAX_AGE = 180  # days

    # 2-way encryption/decryption algorithm for obscuring IDs
    OBSCURE_SALT = os.environ.get("OBSCURE_SALT")

    # for AES 2-way encryption (for order payment data stored in the db)
    RANDOM_STRING = os.environ.get("RANDOM_STRING")

    TEST_EMAILS = [
        os.environ.get('STORE_EMAIL'),
    ]

    # survey platform API credentials
    SURVEY_API_KEY = os.environ.get("SURVEY_API_KEY")
    SURVEY_API_URL = os.environ.get("SURVEY_API_URL")
    SURVEY_SEGMENT = os.environ.get("SURVEY_SEGMENT")

    # vantiv prelive config
    WORLDPAY_JS = os.environ.get("WORLDPAY_JS")
    WORLDPAY_APPLEPAY_JS = os.environ.get("WORLDPAY_APPLEPAY_JS")
    WORLDPAY_EPROTECT_URL = os.environ.get("WORLDPAY_EPROTECT_URL")
    WORLDPAY_PAYPAGE_ID = os.environ.get("WORLDPAY_PAYPAGE_ID")
    WORLDPAY_APPLEPAY_PAYPAGE_ID = os.environ.get("WORLDPAY_APPLEPAY_PAYPAGE_ID")
    WORLDPAY_MERCHANTID = os.environ.get("WORLDPAY_MERCHANTID")
    WORLDPAY_STYLE = os.environ.get("WORLDPAY_STYLE")
    WORLDPAY_USER = ""
    WORLDPAY_PASSWORD = ""
    WORLDPAY_ENDPOINT = ""

    # sandbox Paypal creds.  production ones are in production block below
    WPP_VERSION = os.environ.get("WPP_VERSION")
    WPP_PAYMENTACTION = os.environ.get("WPP_PAYMENTACTION")
    WPP_USER = os.environ.get("WPP_USER")
    WPP_PWD = os.environ.get("WPP_PWD")
    WPP_SIG = os.environ.get("WPP_SIG")
    WPP_PAYPAL_URI = os.environ.get("WPP_PAYPAL_URI")
    WPP_NVP_URI = os.environ.get("WPP_NVP_URI")

    # applepay prelive creds.  production ones in production block below
    APPLEPAY_MERCHID_ENDPOINT = os.environ.get("APPLEPAY_MERCHID_ENDPOINT")
    APPLEPAY_MERCHID = os.environ.get("APPLEPAY_MERCHID")
    APPLEPAY_MERCHID_KEY = os.environ.get("APPLEPAY_MERCHID_KEY")
    APPLEPAY_MERCHID_CERT = os.environ.get("APPLEPAY_MERCHID_CERT")

    # vertex credentials - 'D' prefix company codes are for development
    VERTEX_TOKEN_ENDPOINT = os.environ.get("VERTEX_TOKEN_ENDPOINT")
    VERTEX_REST_ENDPOINT = os.environ.get("VERTEX_REST_ENDPOINT")
    VERTEX_SALE_URI = os.environ.get("VERTEX_SALE_URI")
    VERTEX_SCOPE = os.environ.get("VERTEX_SCOPE")
    VERTEX_GRANT_TYPE = os.environ.get("VERTEX_GRANT_TYPE")

    VERTEX_API_KEY = os.environ.get("VERTEX_API_KEY")
    VERTEX_API_PASS = os.environ.get("VERTEX_API_PASS")
    VERTEX_CLIENT_ID = os.environ.get("VERTEX_CLIENT_ID")
    VERTEX_CLIENT_SECRET = os.environ.get("VERTEX_CLIENT_SECRET")

    VERTEX_COMPANY_CODE = "200"
    VERTEX_SELLER_COMPANY = "FlaskCommerce"
    VERTEX_SELLER_ADDRESS1 = "1234 Test St."
    VERTEX_SELLER_ADDRESS2 = ""
    VERTEX_SELLER_CITY = "Springfield"
    VERTEX_SELLER_STATE = "MA"
    VERTEX_SELLER_ZIP = "01101"
    VERTEX_SELLER_COUNTRY = "USA"

    VERTEX_ACTIONS = "VIEW, CHECKOUT, PAYMENT, CONFIRMATION, COMPLETE, ORDERBUILDER, AJAX_ORDERBUILDER, CL_TOTALS, EXPRESSCHECKOUT"
    VERTEX_DISCOUNT_EXCLUDES = "GC9999, EC9999"
    VERTEX_COUNTRY_EXCLUDES = "CANADA, CAN, CA, CN"

    CRO_ACCOUNT_ID = os.environ.get("CRO_ACCOUNT_ID")

    PRODUCTION = False
    FAILOVER = False


class development(Config):
    STORE_EMAIL = os.environ.get('STORE_EMAIL')
    APP_ROOT = "/project/flask_app"
    PUBLIC_HTML = "/project/public_html"
    DEVELOPMENT = True
    DEBUG = True
    STORE_URL = os.environ.get("DEV_URL")
    INTERNAL_IP = os.environ.get("DEV_URL")
    GTM_ID = os.environ.get("DEV_GTM_ID")
    GA_MEASUREMENT_ID = os.environ.get("DEV_GA_MEASUREMENT_ID")
    GA_MEASUREMENT_PROTOCOL_SECRET = os.environ.get("DEV_GA_MEASUREMENT_PROTOCOL_SECRET")
    MAIL_SERVER = os.environ.get('DEV_MAIL_SERVER')
    MAIL_PORT = os.environ.get('DEV_MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('DEV_MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('STORE_EMAIL')
    MAIL_PASSWORD = os.environ.get('DEV_MAIL_PASSWORD')
    DEFAULT_MAIL_SENDER = os.environ.get('STORE_EMAIL')
    APPLEPAY_MERCHID_INIT_CONTEXT = "dev.flaskcommerce.local"


class staging(Config):
    APP_ROOT = "/home/flaskcommerce/flask_app"
    PUBLIC_HTML = "/home/flaskcommerce/public_html"
    DEVELOPMENT = True
    DEBUG = True
    CACHE_TYPE = "RedisCache"
    STORE_URL = "https://flaskcommerce.thewhiteroom.com"
    GTM_ID = os.environ.get("STAGING_GTM_ID")
    GA_MEASUREMENT_ID = os.environ.get("STAGING_GA_MEASUREMENT_ID")
    GA_MEASUREMENT_PROTOCOL_SECRET = os.environ.get("STAGING_GA_MEASUREMENT_PROTOCOL_SECRET")
    MAIL_SERVER = os.environ.get('STAGING_MAIL_SERVER')
    MAIL_PORT = os.environ.get('STAGING_MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('STAGING_MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('STORE_EMAIL')
    MAIL_PASSWORD = os.environ.get('STAGING_MAIL_PASSWORD')
    DEFAULT_MAIL_SENDER = os.environ.get('STORE_EMAIL')
    APPLEPAY_MERCHID_INIT_CONTEXT = "flaskcommerce.thewhiteroom.com"


class production(Config):
    APP_ROOT = "/home/flaskcommerce/flask_app"
    PUBLIC_HTML = "/home/flaskcommerce/public_html"
    DEVELOPMENT = False
    DEBUG = False
    CACHE_TYPE = "RedisCache"
    STORE_URL = "https://flaskcommerce.thewhiteroom.com"
    GTM_ID = os.environ.get("PROD_GTM_ID")
    GA_MEASUREMENT_ID = os.environ.get("PROD_GA_MEASUREMENT_ID")
    GA_MEASUREMENT_PROTOCOL_SECRET = os.environ.get("PROD_GA_MEASUREMENT_PROTOCOL_SECRET")
    MAIL_SERVER = os.environ.get('PROD_MAIL_SERVER')
    MAIL_PORT = os.environ.get('PROD_MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('PROD_MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('STORE_EMAIL')
    MAIL_PASSWORD = os.environ.get('PROD_MAIL_PASSWORD')
    PRODUCTION = True

