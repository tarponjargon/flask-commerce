""" Export orders to the survey platform.   """

import re
import json
import requests
import json
import os
import time
from datetime import datetime
import atexit
from pprint import pprint
from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import md5_encode, write_pid_file, remove_pid_file, convert_to_ascii
from flask_app.modules.user import get_id_by_email

@current_app.cli.command("update_survey")
def update_survey():
  """
  Export orders to the survey platform
  """

  # check/set PID file and error/exit if one exists
  pid_file = 'tmp/ysurvey_orders_persist.pid'
  if os.path.exists(pid_file):
    current_app.logger.error("PID file {} exists. Exiting.".format(pid_file))
    exit(1)
  pidstatus = write_pid_file(pid_file, os.getpid())
  #print('pidstatus:', pidstatus)
  atexit.register(remove_pid_file, pid_file)

  errors = []
  contacts = []
  order_group = []
  post_url = current_app.config["SURVEY_API_URL"]
  headers = {
      "accept": "text/plain",
      "content-type": "application/json",
      "x-apikey": current_app.config["SURVEY_API_KEY"],
  }

  # select orders from orders_products b/c orders.timestamp is updated whenever
  # the record is touched and is not reliable
  sql = """
      SELECT
        orders_products.order_id,
        DATE_FORMAT(orders_products.timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp
      FROM orders_products
      GROUP BY order_id
    """
  if current_app.config['PRODUCTION']:
    sql = """
      SELECT
        orders_products.order_id,
        DATE_FORMAT(orders_products.timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp
      FROM orders_products
      WHERE timestamp >= CURDATE() - INTERVAL 1 DAY
      AND timestamp < CURDATE()
      GROUP BY order_id
    """
  q = DB.fetch_all(sql)['results']

  for res in q:
      order_group.append({
          "order_id": res['order_id'],
          "created_at": res['timestamp']
      })

  if not order_group:
    print ("No orders to persist to survey")
    return None

  order_ids= [i['order_id'] for i in order_group]
  orders = DB.fetch_all(
      """
        SELECT
          LOWER(TRIM(orders.bill_email)) AS email,
          TRIM(orders.bill_fname) AS first_name,
          TRIM(orders.bill_lname) AS last_name,
          orders.order_id,
          orders.total_order,
          UPPER(orders.coupon_code) AS coupon_code,
          NULL as created_at,
          customers.optin
        FROM orders, customers
        WHERE order_id IN %(order_ids)s
        AND orders.bill_email = customers.bill_email
        AND customers.optin = 'yes'
        ORDER BY order_id ASC
      """, { 'order_ids': tuple(order_ids) }
  )
  for result in orders['results']:

    order_id = result['order_id']
    created_at = next(i['created_at'] for i in order_group if i['order_id'] == order_id)
    order = {
      'email': result['email'],
      'name': convert_to_ascii(result['first_name']) + ' ' + convert_to_ascii(result['last_name']),
      'segment': current_app.config['SURVEY_SEGMENT'],
      'location_orderid_c': current_app.config['ORDER_PREFIX'] + str(order_id),
      'location_ordertime_c': created_at,
      'location_coupon_c': result['coupon_code'],
      'location_customer_c': 'new',
      'location_skuids_c': ''
    }

    order_products = DB.fetch_all("""
      SELECT unoptioned_skuid AS skuid
      FROM orders_products
      WHERE order_id = %s
    """, (order_id))['results']

    # add the skus on the order as a string list
    skuidslist = [i['skuid'] for i in order_products]
    order['location_skuids_c'] = ', '.join(skuidslist)

    # check if the customer has placed an order before
    query = DB.fetch_one(
      """
        SELECT
          COUNT(*) AS existing
        FROM orders
        WHERE bill_email = %s
      """, (result['email'])
    )
    if query.get('existing') > 1:
      order['location_customer_c'] = 'existing'

    contacts.append(order)

  payload = {
    "contacts": contacts
  }


  # post contacts to survey
  response = requests.post(post_url, json=payload, headers=headers)
  dt_object = datetime.fromtimestamp(time.time())
  formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')

  if response.status_code >= 300:
    errors.append("Error persisting order {}: {} {}".format(order_id, response.text, order))
  else:
    print("\nPOST request {} RESPONSE CODE {}".format(post_url, response.status_code))
    print("\nREQUEST HEADERS:\n")
    pprint(response.request.headers)
    print("\nREQUEST BODY:\n")
    print(json.dumps(payload, indent=2))
    print("\nRESPONSE HEADERS:\n")
    for key, value in response.headers.items():
      print(f'{key}: {value}')
    print("\n\n")

  if len(errors):
    current_app.logger.error("Errors persisting orders to survey: {}".format(errors))
    out = "{} Orders NOT persisted to survey. errors: {}".format(
      formatted_datetime,
      errors
    )
    print(out)
    exit(1)


