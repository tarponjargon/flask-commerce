from slugify import slugify
from pprint import pprint
from flask import current_app
from flask_app.modules.extensions import DB

def path_exists(path):
  """ check if given path exists
  Args:
    path (string): path to check

  Returns:
    str: the SKUID of the product that the path belongs to, else empty string
  """

  q = DB.fetch_one("""
      SELECT skuid AS path_exists
      FROM product_urls
      WHERE path = %s
    """, (path))

  return q.get('path_exists', "")

def path_exists_for_product(path, skuid):
  """ check if given path exists for this SKUID
  SQL uses regex because we need to check for the path and an optional number at the end
  (denoting a workaround for a naming conflict)

  Args:
    path (string): path to check
    skuid (string): skuid to check

  Returns:
    int: id of the record, 0 otherwise
  """

  q = DB.fetch_one("""
      SELECT id AS path_exists
      FROM product_urls
      WHERE skuid = %(skuid)s
      AND path RLIKE %(path_regex)s
    """, (
      {
        'skuid': skuid,
        'path_regex': '^' + path + r'(-\d{1,4})?$'
      }
    ))

  #print("path exists {}".format(q.get('path_exists', 0)))
  return q.get('path_exists', 0)

def create_path(slug, skuid):
  return "/products/{}/{}".format(slug, skuid)

def create_alternate_path(slug):
  """ when there's a naming conflict, append an incrementing number to the path

  Args:
    slug (string): the slugified name

  Returns:
    string: the new path
  """

  loopcount = 0
  path = ""
  while True:
    loopcount += 1
    new_path = create_path(slug + '-' + str(loopcount))
    exists_skuid = path_exists(new_path)

    # break out if no result or we've reached the max tries
    if not exists_skuid or loopcount == 1000:
      path = new_path
      break
    else:
      print('checking if alternate path: {} exists, I found that it does exist for SKUID {}'.format(new_path, exists_skuid))

  return path

def delete_missing_products():
  """ delete paths for products that no longer exist """

  # this causes a "Lost Conenction"c issue
  # q = DB.delete_query("""
  #   DELETE FROM product_urls
  #   WHERE skuid NOT IN
  #     (SELECT SKUID FROM products GROUP BY SKUID)
  #   """)
  results = DB.fetch_all("""
    SELECT skuid FROM product_urls
  """)['results']

  deleted = 0
  for res in results:
    skuid = res.get('skuid')
    q = DB.fetch_one("""
      SELECT SKUID FROM products WHERE SKUID = %s
    """, skuid)
    if not q.get('SKUID'):
      q = DB.delete_query("""
        DELETE FROM product_urls
        WHERE skuid = %s
      """, skuid)
      deleted += 1

  print("Deleted {} missing products from product_urls".format(deleted))


def slugify_all_products():
  """ slugify all products and create paths for them

  Returns:
    tuple: the number of new paths created and a list of errors
  """
 # loop all products
  products = DB.fetch_all("SELECT SKUID AS skuid, NAME AS name FROM products GROUP BY SKUID")['results']

  new_paths = 0
  errors = []

  # to account for new products and products that have name changes...
  # at runtime, slugify every product name and create a path.  check if that path exists for the product
  # (with optional number at the end to account for naming conflicts).  If that exists, skip to next product, it's all good.
  # if it doesn't exist, check if the path exists for another product.  If it does, create an alternate path
  # with an integer to it.  insert the path.
  for product in products:
    skuid = product.get('skuid', "").strip()
    name = product.get('name', "").strip()
    name = name.replace("'", '')
    slug = slugify(name)

    path = create_path(slug, skuid)
    # pprint("name: {} | slug: {} | path {} | skuid {}".format(name, slug, path, skuid))

    # if the path exists for this product, no need to do anything
    exists_id = path_exists_for_product(path, skuid)
    # print('exists_id: {}'.format(exists_id))
    if exists_id > 0:
      continue

    # check if it exists (as another product)
    other_skuid = path_exists(path)
    if other_skuid:
      print('checking SKUID {}, I found the same path exists for another SKUID: {} path: {}'.format(skuid, other_skuid, path))
      path = create_alternate_path(slug)

    if not path:
      errors.append('Error creating path for skuid: {}, name: {}'.format(skuid, name))
      continue

    # insert the path
    ins_id = DB.insert_query("INSERT INTO product_urls (skuid, path) VALUES (%s, %s)", (skuid, path))
    if ins_id:
      new_paths = new_paths + 1
      # print('inserted path {} into: {} for SKUID'.format(path, ins_id, skuid))
    else:
      errors.append('Error inserting path for skuid: {}, path {}'.format(skuid, path))

  # do some cleanup
  # delete_missing_products()

  return (new_paths, errors)


