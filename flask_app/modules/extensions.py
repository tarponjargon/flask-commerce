""" Extensions

For loading flask extensions.  In a separate module from create_app to avoid circular imports.
"""

from flask import current_app
import redis
from werkzeug.routing import BaseConverter
from flask_compress import Compress
from flask_caching import Cache
from flask_session import Session
from flask_mail import Mail
from flask_app.modules.database.flask_pymysql import MySQL

from .database.db_manager import DBManager

sess = Session()
compress = Compress()
db = MySQL()
cache = Cache()
mail = Mail()
DB = DBManager(db)
redis_cart = redis.Redis(
    host=current_app.config["CART_REDIS_HOST"],
    port=current_app.config["CART_REDIS_PORT"],
    db=current_app.config["CART_REDIS_DB"],
)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        """Allows regex to be used in flask routes"""
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
