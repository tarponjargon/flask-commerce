""" Functions related to the order ID """

from flask import current_app
from flask_app.modules.extensions import DB
from pymysql import Error


def get_order_id():
    """Order IDs are kept as a value in table 'orderseq'.  This function is a transaction
    that adds 1 to the value, then selects and returns the value to be used as the order ID

    Returns:
      int: The order ID
    """
    order_id = 0
    with DB.db.connection.cursor() as cursor:
        cursor.execute("SET autocommit=0")
        cursor.execute("START TRANSACTION")

        try:
            cursor.execute("UPDATE orderseq SET seqnum=seqnum+1")
            cursor.execute("SELECT seqnum FROM orderseq")
            order_id = cursor.fetchone()[0]

        except Error as e:
            current_app.logger.error(f"ERROR generating order ID {e}")
            cursor.execute("ROLLBACK")
            return order_id

        cursor.execute("COMMIT")
        cursor.execute("SET autocommit=1")

    return order_id
