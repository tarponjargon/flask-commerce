# import re
from flask import current_app

# from flask_app.modules.extensions import mysql
# from pymysql import Error
# from pymysql.converters import escape_string
# from pymysql.err import IntegrityError, ProgrammingError, InternalError
# from pymysql.cursors import DictCursor


# class DBM(object):
#     """Contains functions for running raw SQL queries"""

#     def __init__(self, mysql):
#         self.db = mysql

#     def esc(self, text):
#         """Escapes strings for use in SQL queries

#         Args:
#           test (str): The text to be escaped

#         Returns:
#           str: The escaped text
#         """

#         if isinstance(text, str):
#             # these substitutions may be specific to sqlalchemy...
#             # text = re.sub(re.compile("%+"), "%", text)
#             # text = text.replace("%", "%%")
#             return escape_string(text)
#         elif text is None:
#             return ""
#         else:
#             return text

#     def fetch_one(self, query, params=None):
#         """Helper method for running a SQL query that returns a single result

#         Args:
#           query (str): The query to run.  Make sure it is SQL-safe

#         Returns:
#           dict: The query result with the colums as keys and field values as values.  Dict is empty if none.

#         Example:
#           { 'skuid': 'HB0001' }

#         Raises:
#           pymysql.err.ProgrammingError
#           pymysql.err.IntegrityError
#           pymysql.err.InternalError
#           pymysql.Error: Generic PyMysql error
#         """
#         result = {}
#         try:
#             with mysql.connection.cursor(cursor=DictCursor) as cursor:
#                 cursor.execute(query, params)

#                 # Fetch all the records from SQL query output.
#                 # results are an array of dictionaries, fieldnames are the keys in each dict
#                 r = cursor.fetchone()

#                 if r:
#                     result = r

#                 # log the post-compiled query if the config calls for it
#                 if r and current_app.config["PYMYSQL_LOG_QUERY"]:
#                     current_app.logger.warn("QUERY LOG:")
#                     current_app.logger.warn(cursor.mogrify(query, params))

#         except ProgrammingError as e:
#             current_app.logger.error(f"MySQL ProgrammingError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except IntegrityError as e:
#             current_app.logger.error(f"MySQL IntegrityError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except InternalError as e:
#             current_app.logger.error(f"MySQL InternalError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except Error as e:
#             current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))

#         return result

#     def fetch_all(self, query, params=None):
#         """Helper method for running a SQL query that returns many results

#         If SQL_CALC_FOUND_ROWS is used in the select query, an extra attribute is added
#         to the results that will give is the total # of hits as if there were no LIMIT clause

#         Args:
#           query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
#           params (dict): a dictionary of the named parameters to swap into the query

#         Returns:
#           dict: A dictionary containing the number of rows and a list of the results.
#           dict['calc_rows'] will be 0 and the list will be empty if no matches

#         Example:
#           {
#             'results': [
#               {'skuid': HB0001'},
#               {'skuid': HB0002'},
#               {'skuid': HB0002'}
#             ],
#             'calc_rows': 3
#           }

#         Raises:
#           pymysql.err.ProgrammingError
#           pymysql.err.IntegrityError
#           pymysql.err.InternalError
#           pymysql.Error: Generic PyMysql error
#         """
#         data = {"results": [], "calc_rows": 0}
#         try:
#             with mysql.connection.cursor(cursor=DictCursor) as cursor:
#                 cursor.execute(query, params)

#                 # Fetch all the records from SQL query output.
#                 # results are an array of dictionaries, fieldnames are the keys in each dict
#                 r = cursor.fetchall()

#                 for row in r:
#                     data["results"].append(row)

#                 if "SQL_CALC_FOUND_ROWS" in query:
#                     cursor.execute("SELECT FOUND_ROWS() as FOUND_ROWS")
#                     res = cursor.fetchone()
#                     data["calc_rows"] = res["FOUND_ROWS"] if res and "FOUND_ROWS" in res else 0

#                 # log the post-compiled query if the config calls for it
#                 if r and current_app.config["PYMYSQL_LOG_QUERY"]:
#                     current_app.logger.warn("QUERY LOG:")
#                     current_app.logger.warn(cursor.mogrify(query, params))

#         except ProgrammingError as e:
#             current_app.logger.error(f"MySQL ProgrammingError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except IntegrityError as e:
#             current_app.logger.error(f"MySQL IntegrityError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except InternalError as e:
#             current_app.logger.error(f"MySQL InternalError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except Error as e:
#             current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))

#         return data

#     def update_query(self, query, params=None):
#         """Helper method for running an UPDATE query

#         Args:
#           query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
#           params (dict): a dictionary of the named parameters to swap into the query

#         Returns:
#           int: The number of rows affected.  A 0 value indicates failure.

#         Raises:
#           pymysql.err.ProgrammingError
#           pymysql.err.IntegrityError
#           pymysql.err.InternalError
#           pymysql.Error: Generic PyMysql error
#         """
#         rows = 0
#         try:
#             with mysql.connection.cursor() as cursor:
#                 cursor.execute(query, params)
#                 rows = cursor.rowcount

#         except ProgrammingError as e:
#             current_app.logger.error(f"MySQL ProgrammingError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except IntegrityError as e:
#             current_app.logger.error(f"MySQL IntegrityError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except InternalError as e:
#             current_app.logger.error(f"MySQL InternalError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except Error as e:
#             current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))

#         return rows

#     def insert_query(self, query, params=None):
#         """Helper method for running an INSERT query

#         Args:
#           query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
#           params (dict): a dictionary of the named parameters to swap into the query

#         Returns:
#           int: The id of the inserted row.  A 0 value indicates failure.

#         Raises:
#           pymysql.err.ProgrammingError
#           pymysql.err.IntegrityError
#           pymysql.err.InternalError
#           pymysql.Error: Generic PyMysql error
#         """
#         id = 0
#         try:
#             with mysql.connection.cursor() as cursor:
#                 cursor.execute(query, params)
#                 id = cursor.lastrowid

#         except ProgrammingError as e:
#             current_app.logger.error(f"MySQL ProgrammingError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except IntegrityError as e:
#             current_app.logger.error(f"MySQL IntegrityError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except InternalError as e:
#             current_app.logger.error(f"MySQL InternalError: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))
#         except Error as e:
#             current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
#             current_app.logger.error("APPROX. QUERY: " + self.create_debug_query(query, params))

#         return id

#     def delete_query(self, query, params=None):
#         """Delete and Update are the same at this level, this is just an alias"""
#         return self.update_query(query, params)

#     def create_debug_query(self, query, params=None):
#         """PyMySQL doesn't appear to have a method for printing a complete,
#         parameterized query *IF* the SQL fails.  This function assembles a query by merging in the named
#         parameters.  May not produce actual usable SQL.  It's just to show a rough idea of the SQL for debug pruposes

#         Args:
#           query (str): The query that was executed
#           params (dict): A dictionary of the named parameters

#         Returns:
#           str: The query
#         """

#         if not query or not isinstance(query, str):
#             return query
#         debug_q = query
#         if params and isinstance(params, dict):
#             for k, v in params.items():
#                 repl_key = "%(" + k + ")s"
#                 debug_q = debug_q.replace(repl_key, str(v))

#         return debug_q


@current_app.cli.command("test1")
def test1():
    pass
    # DB = DBM(mysql)
    # query1 = "INSERT INTO login SET customer_id = %(customer_id)s, client = %(client)s, websource = %(websource)s, keyword = %(keyword)s"
    # params = {"customer_id": 1, "client": "12", "websource": "ABC123", "keyword": "RORY"}
    # r = DB.update_query(query1, params)
    # print(r)
