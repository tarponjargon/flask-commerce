import os
import atexit
from pprint import pprint
from flask import current_app
from flask_app.modules.helpers import write_pid_file, remove_pid_file
from flask_app.modules.product.slugify import slugify_all_products, delete_missing_products

@current_app.cli.command("slugify_products")
def slugify_products():

  # check/set PID file and error/exit if one exists
  pid_file = 'tmp/slugify_products.pid'
  if os.path.exists(pid_file):
    current_app.logger.error("PID file {} exists. Exiting.".format(pid_file))
    exit(1)
  pidstatus = write_pid_file(pid_file, os.getpid())
  #print('pidstatus:', pidstatus)
  atexit.register(remove_pid_file, pid_file)

  new_paths, errors = slugify_all_products()

  print('Done. New paths created: {}'.format(new_paths))
  if errors:
    pprint('Errors:')
    pprint(errors)
    exit(1)

@current_app.cli.command("cleanup_slugs")
def cleanup_slugs():
  # delete records from product_urls that are not in products

  delete_missing_products()
  print('Done.')
