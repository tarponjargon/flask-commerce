""" Helpers

Helpers module
"""
import subprocess
import os
import json
from datetime import datetime
from obscure import Obscure
from urllib.parse import unquote
import uuid
from flask import request, current_app, g
from flask_app.modules.extensions import DB, cache
from boltons.iterutils import remap
import babel.numbers
import re
import math
import random
import string
import hashlib
from pymage_size import get_image_size
from unidecode import unidecode
from html import unescape

def validate_skuid(input_string):
    """Validate that the input string matches the pattern for a SKUID

    Args:
      input_string (str): The string to validate

    Returns:
      bool: True if the string passed SKUID validation, False if not
    """

    if not input_string or not isinstance(input_string, str):
        return False

    if len(input_string) > 128:
        return False

    pattern = r'^[a-zA-Z0-9-/_]+$'
    if re.match(pattern, input_string):
        return True
    else:
        return False

def md5_encode(message):
  """ Simply return a md5-encoded version of given string

  Args:
    message (str): the string to encrypt

  Returns:
    str: MD5-encrypted version of message
  """

  if not message or not isinstance(message, str):
    return message

  return hashlib.md5(message.lower().encode("utf-8")).hexdigest()

def get_random_string(length=10):
    """Create a random string using letters and numbers

    Args:
      length (num): The length of the string to return

    Returns:
      str: The random string
    """
    chars = string.ascii_letters + string.digits
    return "".join((random.choice(chars)) for x in range(length))


def encode_id(id):
    """Encode a given ID with 2-way encryption package 'obscure'

    Args:
      id (str): The id you want obscured

    Returns:
      str: The obscured id
    """
    if not id:
        return None
    obscure = Obscure(current_app.config["OBSCURE_SALT"])

    return obscure.encode_hex(id)


def decode_id(encoded_id):
    """Decode a given ID with 2-way encryption package 'obscure'

    Args:
      encoded_id (str): The id to un-obscure

    Returns:
      str: The decoded (un-obscured) id
    """
    if not id:
        return None
    obscure = Obscure(current_app.config["OBSCURE_SALT"])

    return obscure.decode_hex(encoded_id)


def double_encode(mystring):
    """Replace % character in given string with %25

    Args:
      mystring (str): The string to double encode

    Returns:
      str: the double-encoded string
    """
    if not isinstance(mystring, str):
        return mystring

    mystring = mystring.replace("%", "%25")

    return mystring


def replace_double_quote(mystring):
    """replace any instances of double quotes with the html entity

    Args:
      mystring (str): The string to replace quotes in

    Returns:
      str: the new string with the html entity for quotes
    """
    if not isinstance(mystring, str):
        return mystring
    return mystring.replace('"', "&quot;")


def sanitize(mystring):
    """unencode, escape unsafe chars to avoid SQL, XSS

    Args:
      mystring (str): The string to sanitize

    Returns:
      str: the sanitized string
    """

    if isinstance(mystring, str):
        mystring = unquote(mystring)
        mystring = mystring.strip()
        mystring = re.sub(r"\s+", " ", mystring)
        mystring = mystring.replace("<", "&lt;")
        mystring = mystring.replace(">", "&gt;")
        mystring = mystring.replace("'", "&apos;")
        mystring = mystring.replace('"', "&quot;")
        mystring = mystring.replace("&", "&amp;")

        # handles the inevitable instances of chars encoded multiple times
        mystring = re.sub(re.compile("&amp;(amp;)+quot;", re.IGNORECASE), "&quot;", mystring)
        mystring = re.sub(re.compile("&amp;quot;", re.IGNORECASE), "&quot;", mystring)
        mystring = re.sub(re.compile("&amp;(amp;)+apos;", re.IGNORECASE), "&apos;", mystring)
        mystring = re.sub(re.compile("&amp;apos;", re.IGNORECASE), "&apos;", mystring)
        mystring = re.sub(re.compile("&amp;(amp;)+", re.IGNORECASE), "&amp;", mystring)
        mystring = re.sub(re.compile("&amp;amp;", re.IGNORECASE), "&amp;", mystring)
        mystring = re.sub(re.compile("&amp;(amp;)+gt;", re.IGNORECASE), "&gt;", mystring)
        mystring = re.sub(re.compile("&amp;gt;", re.IGNORECASE), "&gt;", mystring)
        mystring = re.sub(re.compile("&amp;(amp;)+lt;", re.IGNORECASE), "&lt;", mystring)
        mystring = re.sub(re.compile("&amp;lt;", re.IGNORECASE), "&lt;", mystring)

    return mystring


def create_uuid():
    """create a UUID

    Returns:
      str: The UUID
    """
    return str(uuid.uuid4())


def match_uuid(string):
    """checks if string matches a UUID pattern

    Args:
      string (str): UUID as string

    Returns:
      bool: True or False
    """

    uuid_pattern = re.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    if uuid_pattern.match(string):
        return True
    else:
        return False


def validate_email(email):
    """E-Mail validation function

    Args:
      email (str): The e-mail address

    Returns:
      bool: True for successful match, False otherwise.
    """

    if not email or not isinstance(email, str):
        return False
    email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if email_pattern.match(email):
        return True
    else:
        return False


def validate_phone(phone):
    """Validation function for US and Canada phone number formats

    Args:
      phone (str): The phone number

    Returns:
      bool: True for successful match, False otherwise.
    """

    if not phone or not isinstance(phone, str):
        return False
    phone_pattern = re.compile(r"^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")
    if phone_pattern.match(phone):
        return True
    else:
        return False


def format_currency(number):
    """Formats currency, includes $ sign

    Args:
      number: The number to format

    Returns:
      str: The formatted currency, prefixed by a $
    """
    if not is_number(number):
        return number

    return babel.numbers.format_currency(number, "USD", locale="en_US")


def quote_list(lst=None):
    """Takes a list and transforms to a SQL-safe string of quoted values

    Args:
      lst (list): THe list to be joined and quoted

    Returns:
      string: A string of quoted values suitable for use in a SQL IN() clause (for example)
    """

    if not lst or not isinstance(lst, list):
        return None

    return ",".join(map(lambda x: "'%s'" % DB.esc(x), lst))


def split_to_list(value):
    """Takes a semicolon delimited string and splits to list

    Args:
      value (str): the value to be split

    Returns:
      list: a list of strings
    """
    string_list = []
    if isinstance(value, str):
        string_list = value.split(";")
        string_list = list(filter(None, string_list))  # remove empty list items
        string_list = [x.strip() for x in string_list]  # trim whitespace in list items
        string_list = list(filter(None, string_list))
        return string_list
    else:
        return value


def split_and_quote(value):
    """Wrapper around split_to_list and quote_list.  Takes a semicolon-demin list and converts to an SQL-safe quoted list.

    Args:
      value (str): THe string to be split to a list, then joined and quoted

    Returns:
      string: A string of quoted values suitable for use in a SQL IN() clause (for example) OR an empty quoted string
    """
    if not value:
        return "''"
    return quote_list(split_to_list(value))


def format_rating(val):
    """Format ratings to 1 decimal point

    Args:
      val (str): The value to format

    Returns:
      float: The formatted number or the given value if it's not a number
    """
    if not val or not is_number(val):
        return val
    num = float(val)
    return "{0:.1f}".format(num)


def rating_list(rating):
    """Creates a list of 5 css classes representing ratings

    Args:
      rating (float): The rating

    Returns:
      list: The list of 5 css class names

    Example:
      3.5 stars is represented as:
      ['fa-star', 'fa-star', 'fa-star', 'fa-star-half-empty', 'fa-star-o']
    """

    # css classes of the stars
    star = "fa-star"
    half_star = "fa-star-half-empty"
    empty_star = "fa-star-o"

    rating_array = []
    if not rating or not is_number(rating):
        return rating_array

    rating = float(rating)
    full_stars = math.floor(rating / 1)

    for i in range(full_stars):
        rating_array.append(star)

    if rating - full_stars >= 0.75:
        rating_array.append(star)
    elif rating - full_stars >= 0.3:
        rating_array.append(half_star)

    for i in range(5 - len(rating_array)):
        rating_array.append(empty_star)

    return rating_array


def is_number(s):
    """Determines if given value is a number or not

    Args:
      s (any): The value to evaluate

    Returns:
      bool: True - is a number, False, is not a number
    """
    try:
        if isinstance(s, bool):  # bools are coerced to floats, have to be excepted
            return False
    except Exception as e:
        return False

    try:
        float(s)
        return True
    except Exception as e:
        return False


def is_float(s):
    """checks if given string can be coerced to a float

    Args:
      s (str): The string to evaluate as a float

    Returns:
      bool: True if it can be coerced to a float, false if not
    """
    if not s or not isinstance(s, str):
        return False

    if re.match(r"^-?\d+(?:\.\d+)$", s) is None:
        return False

    return True


def is_int(s):
    """checks if given string can be coerced to an int

    Args:
      s (str): The string to evaluate as an int

    Returns:
      bool: True if it can be coerced as an int, false if not
    """
    if not s or not isinstance(s, str) or s.startswith("0"):
        return False

    try:
        int(s)
    except ValueError:
        return False

    # False if > MAX_SAFE_INTEGER
    if int(s) > 9007199254740991:
        return False

    return True

def strip_non_numeric(s):
    """Strip all non-numeric characters from a given string

    Args:
      s (str): The string to strip

    Returns:
      str: The string with all non-numeric characters removed
    """
    if not s or not isinstance(s, str):
        return s

    return re.sub(r"[^0-9\.]", "", s)

def dedupe(lst):
    """Removes duplicates in a given list

    Args:
      lst (list): The list to dedupe

    Returns:
      list: The deduped ist
    """
    if not lst or not isinstance(lst, list):
        return lst
    output = []
    seen = set()
    for value in lst:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def abbrev(string, length=current_app.config["ABBREV_LENGTH"], strip_html=True):
    """Abbreviates a given string to given length

    Args:
      string (string): The string to abbreviate
      length (int): The length to abbreviate to
      strip_html (bool): Whether or not to strip html in the string

    Returns:
      str: The abbreviated string
    """
    if not string or not isinstance(string, str):
        return string

    if strip_html:
        string = re.sub("<[^<]+?>", "", string)
    return string[:length] + "..."


def strip_html(string):
    """Merely strip the html from given string

    Args:
      string (str): The string to strip the html from

    Returns:
      str: The string, with html tag stripped out
    """
    if not string or not isinstance(string, str):
        return string

    return re.sub("<[^<]+?>", "", string)

def unescape_html(string):
    """Unescape any escaped html (or entities in given string)

    Args:
      string (str): The string to unescape html

    Returns:
      str: The string, with html unescaped
    """
    if not string or not isinstance(string, str):
        return string
    return unescape(string)

def convert_unicode(string):
    """Convert any unicode characters to nearest ASCII equivalent

    Args:
      string (str): The string to examine for unicode

    Returns:
      str: The string, with any unicode chars converted
    """
    if not string or not isinstance(string, str):
        return string
    string = unidecode(string)
    return string

def convert_to_ascii(string):
    """Convert given string to ascii characters

    Args:
      string (str): The string to convert to ascii

    Returns:
      str: The string, converted to ascii
    """
    if not string or not isinstance(string, str):
        return ""

    string = strip_html(unescape_html(convert_unicode(string)))
    if string:
      string = re.sub(r'\s+', ' ', string)
    return string or ""

def dump_json_as_ascii(d):
    """Convert given dict to json string, converting all chars to ascii
    The reason I'm using this in Jinja templates over the built-in 'tojson'
    FOR ld_json data ONLY
    is because the built-in seems to convert apostrophes to unicode

    Args:
      d (dict): The dict to convert to json

    Returns:
      str: The json string, converted to ascii
    """
    if not d:
      return json.dumps({})

    return json.dumps(d, ensure_ascii=True)


def jpg_extension(val):
    """Check if value ends with .jpg.  If not, add it

    USA data (related to images) is not consistent with it's usage of the jpg suffix

    Args:
      val (str): The string to check

    Returns:
      str: The value with .jpg appended
    """
    if not val or not isinstance(val, str):
        return val

    return val if val.endswith(".jpg") else val + ".jpg"


def camelize(string):
    """Convert given string to Camel-case

    Args:
      string (str): The string to convert to camel-case

    Returns:
      str: The camel-cased string
    """
    camelized = string
    if isinstance(string, str):
        components = string.split("_")
        camelized = components[0] + "".join(x.title() for x in components[1:])
    return camelized


def decamelize(string):
    """Convert camel-case to snake-case

    Args:
      string (str): The camel-cased string to convert to snake-case

    Returns:
      str: The snake-cased string
    """
    decamelized = string
    if isinstance(decamelized, str):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", decamelized)
        decamelized = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return decamelized


def serialize(obj=None):
    """Prepare data for consumption by Javascript

    uses boltons.iterutils to recurse into nested data structures.
    add nocasechange=1 to leave keys as snake-case

    Args:
      obj (any): String, list or dict

    Returns:
      object: The inputted object with all keys and values transformed (if necessary)
    """

    if request.args.get("nocasechange"):
        return obj
    if obj is None:
        obj = {}

    newobj = {}
    try:
        newobj = remap(obj, visit=convert_keys)
    except Exception as e:
        current_app.logger.error(f"ERROR problem in serialize {e}")

    return newobj


def convert_keys(path, key, value):
    """Helper function for serialize().  Do not use independently.

    Tells iterutils what to do with each passed key and value

    Args:
      path (str): do not explicitly specify
      key (str): do not explicitly specify
      value (any): do not explicitly specify

    Returns:
      object: for itertools only
    """

    return camelize(key), value


def lowercase_keys(obj):
    """Lowercase all keys in a dictionary (not recusive)

    Args:
      obj (dict): The dictionary to change case of

    Returns:
      dict: The dictionary with keys lowercased
    """
    return {k.lower(): v for k, v in obj.items()}


def image_path(filename, dir="small"):
    """Creates a full path for an image.  The size directory is passed in
    Args:
      filename (str): The image filename.  If not extension is found ".jpg" will be added by default
      dir (str): The size directory to use.  Default is "small" (thumbnail)

    Returns:
      str: the full path to use.
    """
    if not filename:
        return None

    if not re.search(r"\.[A-Za-z0-9]{3,4}$", filename, flags=re.IGNORECASE):
        filename += ".jpg"
    return current_app.config["IMAGE_BASE"] + "/graphics/products/" + dir + "/" + filename


@cache.memoize()
def image_size(path):
    """Wraps pymage_size to performantly get the dimensions of the image
    passed in the path argument

    Args:
      path (str): The full path to the image FROM /public_html (i.e. do not include /public_html), including filename and extension

    Returns:
      tuple: A tuple with width in the first pos, height in the second
    """

    if not path:
        return "", ""
    path = current_app.config["PUBLIC_HTML"] + path
    image_object = None

    try:
        image_object = get_image_size(path)
    except FileNotFoundError as fnf:
        pass
        # current_app.logger.warning("image_size() file not found, " + path)
    except Exception as e:
        pass
        # current_app.logger.error("image_size() error, " + path + " " + str(e))

    if not image_object:
        return "", ""

    return image_object.get_dimensions()


def days_seconds(days):
    """Convert the given number of days into seconds

    Args:
      days: The days to convert to seconds

    Returns:
      int: Days converted to seconds
    """
    if not is_number(days):
        return 0

    return 60 * 60 * 24 * days


def reformat_datestring(datestr):
    """Convert the shorthand date  format like 9/13 (MM/DD) to a full date string

    Assumes year is current year UNLESS given month is less than the current month, and if so 1 year is added

    Args:
      datestr (str): A shorthand date in the format MM/DD, M/DD or M/D

    Returns:
      str: A date in the format YYYYMMDD.  If datestr format is not matched, datestr is returned unformatted
    """
    if not isinstance(datestr, str):
        return datestr

    res = re.search(r"^([0-9]{1,2})/([0-9]{1,2})$", datestr)
    if not res or not len(res.groups()) == 2:
        return datestr

    month = int(res.group(1))
    day = int(res.group(2))
    year = int(datetime.now().strftime("%Y"))
    curmonth = int(datetime.now().strftime("%m"))

    if month < curmonth:
        year = year + 1

    return str(year) + str(month).zfill(2) + str(day).zfill(2)


def days_between(d1, d2):
    """Calculate the number of days between two given date strings

    Args:
      d1 (str): The first date, format YYYYMMDD
      d2 (str): The second date, format YYYYMMDD

    Returns:
      int: The days between the two dates
    """
    if not re.match(r"[0-9]{8}", d1) or not re.match(r"[0-9]{8}", d2):
        return 0

    try:
      d1 = datetime.strptime(d1, "%Y%m%d")
      d2 = datetime.strptime(d2, "%Y%m%d")
    except ValueError:
      return 0
    return abs((d2 - d1).days)

def set_order_note(note):
    """Add an order note to tlist on the cart object, only if not already there

    Args:
      note (str): The order note to add

    Returns:
      bool: True if order note added, False if not
    """
    if not isinstance(note, str) or note in g.messages['notes']:
        return False

    g.messages['notes'].append(note)
    return note in g.messages['notes']

def get_order_notes():
    """Get any order notes

    Returns:
      list: A list of order notes
    """
    # this is a landmine related to why global variables are considered problematic.  order messages *generally* get created
    # when cart functions run like get_discount() get_credit() get_tax()
    # if you call get_order_notes() directly and those functions have not run, g.messages['notes'] will likely be empty.
    # notes should probably be handled with view functions
    cart = g.cart.get_total() # calling this to generate any notes, it calls get_discount() get_credit() get_tax()
    notes = g.messages.get('notes')
    if notes and isinstance(notes, list):
      return notes
    else:
      return []


def get_alphabet():
    """Uppercase letters of the alphabet in list form

    Returns:
      list: The uppercase alphabet as a list
    """

    return [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]


def get_months():
    """A list of month codes and names

    Returns:
      list: A list of dictionaries
    """

    return [
        {"code": "01", "name": "Jan"},
        {"code": "02", "name": "Feb"},
        {"code": "03", "name": "Mar"},
        {"code": "04", "name": "Apr"},
        {"code": "05", "name": "May"},
        {"code": "06", "name": "Jun"},
        {"code": "07", "name": "Jul"},
        {"code": "08", "name": "Aug"},
        {"code": "09", "name": "Sep"},
        {"code": "10", "name": "Oct"},
        {"code": "11", "name": "Nov"},
        {"code": "12", "name": "Dec"},
    ]


def do_cache_clear():
    """clears the cached/memoized objects in redis db"""
    cache.clear()

    resp = {"success": True}
    return resp


def do_category_count():
    """runs the MEGA LEGACY script updatecategories.pl, which
    handles product-to-category assignment (among other small jobs)
    """

    # update product assignments using legacy method
    curdir = os.getcwd()
    fullpath_executable = str(curdir) + "/bin/updatecategories.pl"
    result = subprocess.run([fullpath_executable], capture_output=True, text=True, check=False, timeout=100)

    resp = {"success": True if result.returncode == 0 else False, "output": result.stdout, "error": result.stderr}

    cache.clear()
    return resp

def do_search_feed_count():
    """Count the number of lines in the search feed (if exists).  This is used to determine if the feed is being updated."""

    linecount = 0
    curdir = os.getcwd()
    filepath = str(curdir) + "/public_html/searchspring.csv"
    # count the number of lines in the file
    try:
        with open(filepath, "r") as file:
            linecount = 0
            for line in file:
                linecount += 1
    except FileNotFoundError:
      print ("File not found")

    return linecount


def do_file_sync():
    """shells out to run a shell script which syncs files from fileserver to webserver(s)"""

    # update product assignments using legacy method
    curdir = os.getcwd()
    fullpath_executable = str(curdir) + "/bin/fileserver_sync.sh"
    result = subprocess.run([fullpath_executable], capture_output=True, text=True, check=True, timeout=100)

    resp = {"success": True if result.returncode == 0 else False, "output": result.stdout, "error": result.stderr}

    cache.clear()
    return resp

def invdata_faker(skuid, col='fullsku'):
  """
    3/10/24 - I am getting ProgrammingErrors on LEFT JOINs to invdata.  That happens because 4X an hour
    invdata gets dropped and replaced.  The proper way to handle that would be to re-code the script that is dropping and replacing
    invdata, and have it update the rows instead...BUT that's the way it used to work and it was not resource efficient.

    I am adding a hack below to check if invdata exists first.  If it doesn't, I'm going to update the left join to used faked data so
    that the product or item view is usable.

    This may incorrectly show unavailable items as available, but the fallback is that when they are added to the cart availability will show correctly
    (because invdata will presumably exist at that point, and the cart item availability function will use the real data)

    TODO: either update the inventory importer to work at the row level so invdata always exists OR put this function somewhere
    more meaningful than helpers

    Args:
      skuid (str): The skuid for the inventory you're tyring to look up
      col (str): the column to use in the WHERE clause.  Default is 'fullsku'.  Other option is 'skuid'

    returns:
      str: The SQL query to use if invdata doesn't exist, and empty string if it does
  """
  if not skuid or not isinstance(skuid, str) or not col or not isinstance(col, str) or col not in ['fullsku', 'skuid']:
    return ""

  # check if invdata exists
  res = DB.fetch_one("""
    SELECT COUNT(*) AS `invdata_exists`
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = %(database)s
    AND TABLE_NAME = 'invdata';
  """, { 'database': current_app.config.get('MYSQL_DATABASE')})

  if res.get('invdata_exists') == 1:
    return ""

  if res.get('invdata_exists') != 1:
    # this is fake data so that the product is orderable.  see docstring above for more info
    fake_invdata_sql = """
        SELECT
        nla AS dicontinuesflag,
        9999 AS `count`,
        9999 AS `on_hand`,
        'R1' AS invcode,
        NULL as `date`,
        NULL as `backorder`,
        fullsku AS skuid,
        NULL AS is_preorder
        FROM `options_index` AS invdata
        WHERE invdata.fullsku = '{}'
    """.format(DB.esc(skuid))

    #current_app.logger.info("FALLBACK invdata used {}".format(fake_invdata_sql))

    return fake_invdata_sql

def is_cs_open():

  current_time = datetime.now()
  current_day = datetime.today() # monday=0...sunday=6
  day_of_week = current_day.weekday()
  current_hour = current_time.hour
  if day_of_week < 5 and current_hour >= current_app.config.get('STORE_CS_HOUR_OPEN', 0) and current_hour < current_app.config.get('STORE_CS_HOUR_CLOSE', 0):
    return True

  return False

def write_pid_file(pid_file, pid):
  """ write the current process id to a file

  Args:
    pid_file (str): The full path to the file to write the pid to
    pid (int): The process id to write to the file
  """
  if not pid_file or not pid:
    return ""
  with open(pid_file, 'w') as f:
      f.write(str(pid))
  return f"PID {pid} written to {pid_file}"

def remove_pid_file(pid_file):
  """ remove the pid file if it exists

  Args:
    pid_file (str): The full path to the pid file to remove
  """
  if os.path.exists(pid_file):
      os.remove(pid_file)
      print(f"Removed PID file: {pid_file}")

def is_valid_isbn(isbn):
    """
    Validates if the given string is a valid ISBN-10 or ISBN-13.

    Args:
      isbn (str): The ISBN string to validate.

    Returns:
      bool: True if the ISBN is valid, False otherwise.
    """
    def is_valid_isbn10(isbn10):
        total = 0
        for i, char in enumerate(isbn10[:-1]):
            total += int(char) * (10 - i)

        check_digit = isbn10[-1]
        if check_digit == 'X':
            total += 10
        else:
            total += int(check_digit)

        return total % 11 == 0

    def is_valid_isbn13(isbn13):
        total = 0
        for i, char in enumerate(isbn13):
            if i % 2 == 0:
                total += int(char)
            else:
                total += int(char) * 3

        return total % 10 == 0
    isbn10_pattern = r'^\d{9}[\dX]$'
    isbn13_pattern = r'^\d{13}$'

    # Check if it matches ISBN-10 pattern
    if re.match(isbn10_pattern, isbn):
        return is_valid_isbn10(isbn)

    # Check if it matches ISBN-13 pattern
    if re.match(isbn13_pattern, isbn):
        return is_valid_isbn13(isbn)

    # If neither, it's invalid
    return False