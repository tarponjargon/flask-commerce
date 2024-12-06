import re

def test_order(app, client):
    """Test an order with a regular, unoptioned items (i.e. no variants)"""
    with app.test_request_context():
        from flask_app.modules.extensions import DB

        app.preprocess_request()

        product = DB.fetch_one(
            f"""
              SELECT
                SKUID as skuid
              FROM products
              WHERE INVENTORY != 1
              AND (CUSTOM IS NULL OR CUSTOM = '')
              AND (OPTIONS IS NULL OR OPTIONS = '')
              ORDER BY RAND()
              LIMIT 1
            """
        )
        skuid = product.get('skuid')

        print("Testing order of item " + skuid)
        post_data = {
          'LOGINPASS': '1',
          'bill_fname': 'Rory',
          'bill_lname': "O'Connor",
          'bill_street': '1234 Test Street',
          'bill_street2': '',
          'bill_city': 'Bellingham',
          'bill_state': 'WA',
          'bill_postal_code': '98225',
          'bill_zip_4': '',
          'bill_country': 'USA',
          'bill_email': 'tarponjargon@gmail.com',
          'bill_phone': '3126509324',
          'ship_fname': 'Rory',
          'ship_lname': "O'Connor",
          'ship_street': '1234 Test Street',
          'ship_street2': '',
          'ship_city': 'Bellingham',
          'ship_state': 'WA',
          'ship_postal_code': '98225',
          'ship_country': 'USA',
          'ship_method': '24',
          'payment_method': 'standard',
          'card_type': 'VI',
          'card_month': '04',
          'card_year': '32',
          'worldpay_registration_id': '2137898579424579172',
          'worldpay_vantiv_txn_id': '83993708038025121'
        }
        product_key = 'PRODUCT_' + skuid
        post_data[product_key] = '1'
        response = client.post("/complete", data=post_data)

        assert response.status_code == 200

        # Retrieve HTML content from the response
        html_content = response.data.decode('utf-8')

        # Define a regex pattern to match specific text
        regex_pattern = r'data-test-status="[A-Z]([0-9]{7,8})"'

        # Use re.search to find the first match in the HTML content
        match = re.search(regex_pattern, html_content)

        # Check if a match is found
        order_id = None
        if match:
            order_id = match.group(1)
            print(f"Captured Order ID: {order_id}")

        assert len(order_id) > 6

        # check that the order is in the db
        order = DB.fetch_one("SELECT order_id FROM orders WHERE order_id = %(order_id)s", { 'order_id': order_id })

        assert order_id == str(order.get('order_id'))

        # check that the item ordered is on the order
        item = DB.fetch_one("SELECT skuid FROM orders_products WHERE order_id = %(order_id)s", { 'order_id': order_id })

        assert skuid == item.get('skuid')