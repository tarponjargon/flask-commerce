""" User module

An instantiated User class contains all account data.  Generally
called with the classmethod
"""

import re
import hashlib
from flask import current_app, session
from flask_app.modules.helpers import encode_id, get_random_string, validate_email, md5_encode
from flask_app.modules.http import get_env_vars, session_get
from flask_app.modules.extensions import DB
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.user.wishlist import get_hwlid, get_wishlist


def get_billing_fields():
    """Gets a list of the billing fields on the customer record

    Returns:
      list: A list of the billing fieldnames
    """

    res = DB.fetch_all("SELECT code FROM billing_fields_loop")["results"]
    fields = [i.get("code") for i in res]
    fields.append("optin")
    return fields


def get_shipping_fields():
    """Gets a list of the shipping fields

    Returns:
      list: A list of the shipping fieldnames
    """

    res = DB.fetch_all("SELECT code FROM shipping_fields_loop")["results"]
    fields = [i.get("code") for i in res]
    return fields


def get_id_by_email(email):
    """Gets a customer ID by e-mail address

    Args:
      email (str):  The email to get the customer ID for

    Returns:
      int: The customer ID for the given email
    """
    if not email or not isinstance(email, str):
        return None
    res = DB.fetch_one("SELECT customer_id FROM customers WHERE bill_email LIKE %(email)s", {"email": email})
    return res.get("customer_id")


def password_compare(customer_id, pass_to_check):
    """MD5-hashes given password with stored salt and compares to md5_password in customer record

    Args:
      customer_id (int): The customer ID of the account
      pass_to_check (str):  The password to hash-compare

    Returns:
      bool: True if the hased password matches the stored password hash, False if not
    """

    result = DB.fetch_one(
        "SELECT salt,md5_password FROM customers WHERE customer_id = %(customer_id)s", {"customer_id": customer_id}
    )
    salt = result.get("salt")
    md5_password = result.get("md5_password")
    if not salt or not md5_password:
        return False

    # the password in the db is the md5 sum of the combined md5 sums of the
    # password and the salt
    entered_password_hash = hashlib.md5(pass_to_check.encode("utf-8")).hexdigest()
    salt_hash = hashlib.md5(salt.encode("utf-8")).hexdigest()
    combined = entered_password_hash + salt_hash
    combined = combined.encode("utf-8")
    combined_hash = hashlib.md5(combined).hexdigest()

    # compare combined with what's in the db
    if combined_hash == md5_password:
        return True

    return False


def get_customer_id_by_email(email):
    """Returns customer_id if the customer record exists and has a password

    Args:
      email (str): The E-mail address that is the login for the account

    Returns:
      int: The customer_id if found, else 0
    """
    id = 0
    q = DB.fetch_one(
        """
        SELECT customer_id
        FROM customers WHERE bill_email = %(email)s
        AND (md5_password IS NOT NULL and md5_password != '')
        AND (salt IS NOT NULL and salt != '')
      """,
        {"email": email},
    )
    if q and q.get("customer_id", 0) > 0:
        id = q.get("customer_id")

    return id


def encrypt_password(password):
    """Generates salt and encrypts password using salt and MD5

    Args:
      password (str): The password to encrypt

    Returns:
      tuple: A tuple with the generated salt and the hashed_password)
    """

    salt = get_random_string()
    md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
    md5_salt = hashlib.md5(salt.encode("utf-8")).hexdigest()
    combined = md5_password + md5_salt
    hashed_password = hashlib.md5(combined.encode("utf-8")).hexdigest()

    return (salt, hashed_password)


def create_user(email, password):
    """Creates a new user (customer) with given e-mail and password.  Both should already be format-validated and
    the user should not already exist.  The user "exists" when there is an email address, md5_password and salt
    in the customers table.  It's possible that a record can exist with the email, but if it doesn't
    have an md5_password and salt then it's considered just a contact

    Args:
      email (str): The email (login) of the new user
      password (str): The password for the new account

    Returns:
      int: The customer_id of the new account
    """

    env_vars = get_env_vars()
    (salt, hashed_password) = encrypt_password(password)

    # determine customer ID (there may not be one )
    customer_id = get_id_by_email(email)

    # email can exist as a record and not be an account (no password).  Have to check
    # if the account creation is an insert or an update
    if customer_id:
        ins_or_upd = "UPDATE"
        success = DB.update_query(
            """
              UPDATE customers SET
              md5_password = %(hashed_password)s,
              salt = %(salt)s,
              ins_or_upd = %(ins_or_upd)s,
              `date` = %(dt)s
              WHERE customer_id = %(customer_id)s
              LIMIT 1
            """,
            {
                "hashed_password": hashed_password,
                "salt": salt,
                "ins_or_upd": ins_or_upd,
                "dt": env_vars.get("date"),
                "customer_id": customer_id,
            },
        )
        if not success:
            current_app.logger.error(f"problem creating customer {email} as record update")
            return None
    else:
        ins_or_upd = "INSERT"
        customer_id = DB.insert_query(
            """
              INSERT INTO customers SET
              bill_email = %(email)s,
              md5_password = %(hashed_password)s,
              salt = %(salt)s,
              optin = 'yes',
              ins_or_upd = %(ins_or_upd)s,
              insert_date = %(ts)s,
              `date` = %(dt)s
            """,
            {
                "email": email,
                "hashed_password": hashed_password,
                "salt": salt,
                "ins_or_upd": ins_or_upd,
                "ts": env_vars.get("timestamp"),
                "dt": env_vars.get("date"),
            },
        )
        if not id:
            current_app.logger.error(f"problem creating customer {email} as record insert")
            return None

    record_customer_activity(
        request_type="newaccount",
        ins_or_upd=ins_or_upd,
        email_exists="1" if customer_id else "0",
        email=email,
        capture="N",
    )
    return customer_id


def get_user(customer_id):
    """Load user data from the DB

    Args:
      customer_id (int): The customer_id

    Returns:
      dict: The user data loaded from the db
    """

    fields = ",".join(get_billing_fields())
    sql = f"SELECT {fields} FROM customers WHERE customer_id = %(customer_id)s"
    params = {"customer_id": customer_id}
    return DB.fetch_one(sql, params)


def create_address_hash(firstname="", lastname="", address1="", zip_code=""):
  """ Create a unique hash for a customer using name, address and zip.  this is used to match
  customers to catalog recipients.  If arguments are not passed, grab from session

  Args:
    firstname (str): The first name of the customer
    lastname (str): The last name of the customer
    address1 (str): The street address of the customer
    zip_code (str): The zip code of the customer

  Returns:
    str: The unique hash
  """

  fname = firstname if firstname else session_get("bill_fname", "")
  lname = lastname if lastname else session_get("bill_lname", "")
  addr1 = address1 if address1 else session_get("bill_street", "")
  zipcode = zip_code if zip_code else session_get("bill_postal_code", "")

  if not fname or not lname or not addr1 or not zipcode:
    return ""

  if not len(zipcode) >= 5 or not re.match(r'\d+', zipcode):
    return ""

  if not len(addr1) >= 3:
    return ""

  fullname = str(fname) + " " + str(lname)

  # Remove leading spaces and extract the first word from name
  f_name = re.match(r'^\s*(\S+)', fullname).group(1)

  try:
      # Remove trailing spaces and extract the last word from name
      l_name = re.search(r'(?<=\s)([^ ]*)$', fullname.strip()).group(1)
  except AttributeError:
      l_name = ''

  # Extract the first 5 digits of the zip code
  zip5 = re.search(r'\d+', zipcode).group(0)[:5]

  # Extract the first 3 characters of the address
  adr = addr1[:3]

  # Combine all parts and format the final string
  formatted_str = str(f_name) + str(l_name) + str(zip5) + str(adr)
  formatted_str = re.sub(r'[^\w\s]', '', formatted_str)  # Remove non-alphanumeric characters
  formatted_str = re.sub(r'\s+', '', formatted_str)      # Remove whitespace
  formatted_str = formatted_str.lower()                  # Convert to lowercase
  #print("formatted_str {}".format(formatted_str))

  return md5_encode(formatted_str)

def create_phone_hash(phone=""):
  """ Hash a phone number If not passed, grab from session

  Args:
    phone (str): The phone number to hash

  Returns:
    str: The hashed phone
  """

  ph = phone if phone else session_get("bill_phone", "")

  if not ph or not len(ph) >= 10:
    return ""

  # Remove nun-numeric characters
  ph = re.sub(r'\D', '', ph)
  # Remove leading '1' if present
  ph = re.sub(r'^1', '', ph)
  # Get the last 10 digits
  if not len(ph) >= 10:
    return ""
  ph = ph[-10:]
  #print("formatted_str {}".format(ph))

  return md5_encode(ph)

class User(object):
    def __init__(self, customer_id, user=None):
        if user is None:
            user = {}

        self.customer_id = customer_id
        self.data = user

    def get_user(self):
        """Gets user

        Returns:
          User: The User
        """
        return self.data

    def get_account_data(self):
        """
        Get all data associated with this account.  Used to send to the client as JSON

        Returns:
          dict: The account user details, wishlist, addresses, orders
        """
        if not self:
            return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403

        account = {
            "success": True,
            "error": False,
            "user": {},
            "addresses": [],
            "orders": [],
            "wishlist": {"items": []},
        }

        # populate 'user' key and update session with same keys/vals
        for key, val in self.get_user().items():
            session[key] = val
            account["user"][key] = val

        account["wishlist"] = get_wishlist(get_hwlid(self.customer_id))
        account["addresses"] = self.get_addresses()
        account["orders"] = self.get_order_summary()

        return account

    def get_order_summary(self):
        """
        Get a list of orders for this customer

        Returns:
          list: a list of dictionaries, each being an order
        """
        orders = []
        q = DB.fetch_all(
            """
              SELECT
                order_id,
                DATE_FORMAT(date, '%%Y%%m%%d') AS date,
                total_order,
                ship_fname,
                ship_lname,
                IF(orders.date < DATE_SUB(NOW(), INTERVAL 90 DAY), 'Archived', 'Processing') as orderStatus
              FROM orders
              WHERE customer_id = %(customer_id)s
              ORDER BY timestamp DESC
          """,
            {"customer_id": self.customer_id},
        )

        for res in q["results"]:
            ordno = current_app.config["ORDER_PREFIX"] + str(res.get("order_id"))
            q = DB.fetch_one(
                f"""
                  SELECT `status` FROM status WHERE ordno = '{ordno}' GROUP BY `status`
                """
            )
            orders.append(
                {
                    "id": res.get("order_id"),
                    "date": int(res.get("date")),
                    "totalOrder": float(res.get("total_order")),
                    "shippingFirstname": res.get("ship_fname"),
                    "shippingLastname": res.get("ship_lname"),
                    "orderStatus": q.get("status") if q.get("status") else res.get("orderStatus"),
                }
            )

        return orders

    def get_addresses(self):
        """Get customer addresses in addressbook

        Returns:
          list: A list of dictionaries (each being an address)
        """
        addresses = []
        shipping_fields = get_shipping_fields()
        q = DB.fetch_all(
            """
              SELECT *
              FROM addresses WHERE customer_id = %(customer_id)s
              ORDER BY timestamp DESC
            """,
            {"customer_id": self.customer_id},
        )
        for res in q["results"]:
            address = {"id": encode_id(res.get("address_id"))}
            for field in [i for i in shipping_fields if i != "address_id"]:
                address[field] = res.get(field)
            addresses.append(address)

        return addresses

    def update_account_info(self, values=None):
        if values is None:
            values = {}
        email = values.get("bill_email")
        if not email or not validate_email(email):
            return {
                "success": False,
                "error": True,
                "errors": ["Please enter an E-mail in the format you@yourdomain.com"],
            }

        existing_id = get_customer_id_by_email(email)
        if not self.customer_id == existing_id:
            return {"success": False, "error": True, "errors": ["A different account exists with that e-mail address"]}

        if not values.get("optin") in ["yes", "no"]:
            values["optin"] = "yes"

        # build the SET key = 'value' SQL from the model
        billing_fields = get_billing_fields()
        sql_values = ", ".join([f"{i} = %s" for i in billing_fields])
        sql_params = [values.get(i) for i in billing_fields]
        sql = f"UPDATE customers SET {sql_values},timestamp=NOW() WHERE customer_id = '{DB.esc(self.customer_id)}'"

        success = DB.update_query(sql, tuple(sql_params))
        if not success:
            current_app.logger.error(f"Problem updating account {sql}")
            return {"success": False, "error": True, "errors": ["Problem updating your account.  Please contact us."]}

        record_customer_activity(request_type="updateaccount", email=email, optin=values.get("optin"))

        return {"success": True, "error": False}

    def upsert_address(self, values=None, address_id=None):
        """
        Insert or update address based on existence of address_id.  Address keys come in prefixed with TEMP_.

        Args:
          values (dict): The values of the address to update
          address_id (int): Passed only for an update.  The address id of the address to update

        Returns:
          dict: A success or fail payload to send to the user
        """

        if not values:
            values = {}

        required = ["ship_fname", "ship_lname", "ship_street", "ship_city", "ship_state", "ship_postal_code"]

        # check required
        if not all([values.get("TEMP_" + i) for i in required]):
            return {"success": False, "error": True, "errors": ["Required: name, address 1, city, state, postal code"]}

        # check the address doesn't already exist in another record
        sql_values = " AND ".join([f"{i} LIKE %s" for i in required])
        sql_params = [values.get("TEMP_" + i) for i in required]
        sql_params.insert(0, self.customer_id)
        sql = f"SELECT address_id FROM addresses WHERE customer_id = %s AND {sql_values}"
        q = DB.fetch_one(sql, sql_params)
        if q and q.get("address_id"):
            if (address_id and address_id != q.get("address_id")) or (not address_id):
                return {"success": False, "error": True, "errors": ["This address already exists in your addressbook"]}

        # build the SET key = 'value' SQL from the model
        address_fields = get_shipping_fields()
        sql_values = ", ".join([f"{i} = %s" for i in address_fields])
        sql_params = [values.get("TEMP_" + i) for i in address_fields]
        sql_params.append(self.customer_id)

        sql = None
        if address_id:
            sql_params.append(address_id)
            sql = f"""
              UPDATE addresses SET {sql_values}, timestamp=NOW()
              WHERE customer_id = %s
              AND address_id = %s
            """
        else:
            sql = f"""
              INSERT INTO addresses SET {sql_values},
              customer_id = %s
            """
        success = DB.update_query(sql, sql_params)

        if not success:
            return {"success": False, "error": True, "errors": ["Problem updating your address.  Please contact us."]}

        return {"success": True, "error": False}

    def delete_address(self, address_id):
        """Delete a customer address

        Args:
          address_id (int): The address ID

        Returns:
          dict: A success or fail payload to send to the user
        """

        success = DB.delete_query(
            "DELETE FROM addresses WHERE customer_id = %(customer_id)s AND address_id = %(address_id)s LIMIT 1",
            {"customer_id": self.customer_id, "address_id": address_id},
        )

        if not success:
            return {"success": False, "error": True, "errors": ["Problem deleting your address.  Please contact us."]}

        return {"success": True, "error": False}

    @classmethod
    def from_id(cls, customer_id):
        """Constructor creates User object from customer_id

        Args:
          customer_id (int): The customer ID

        Returns:
          User: the instantiated User object
        """
        user_data = get_user(customer_id)
        if user_data["bill_fname"] == "Shopper":
            user_data["bill_fname"] = ""

        return cls(customer_id, user_data)
