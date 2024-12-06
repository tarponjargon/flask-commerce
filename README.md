# OVERVIEW

This is a Flask-based e-commerce platform developed for a client that has since been purchased by another company.
I've anonymized it for the purposes of open-sourcing.

This codebase came into being because of issues we were running into with a legacy CGI (written in C) e-commerce platform we used. Over the years I had customized
that application to conform very closely with the client's unique set of business rules, but the platform itself was very limited, unsupported and had the traditional
issues associated with CGI. It was also very risky for the business due to a high "bus factor". I know you're not supposed to do rewrites, but CGI platform was simply no longer tenable.

We looked at SaaS options, but ultimately the amount of custom rules we needed to support made migrating to SaaS a painful and costly prospect. Instead, we opted
for a "like-for-like" rewrite of the old platform's functionality, but using modern tech stack (python). By doing a like-for-like I was able to retain
much of the front-end code (which had already been modernized), the database schema, and most of the ad-hoc (scheduled) processes that used the database directly.
This reduced the cost, coimplexity and need for re-training of staff.

I wrote the vast majority of the code, and there's alot of myself (and even my free time) in this. I very much enjoyed coding it, and it gave me a strong sense of ownership over the product.
I monitoried it very closely for errors and constantly debugged. It also worked very well. The site speed improved measurably, and it was much easier on
server resources (a fraction, in fact). Because of the modern tooling, dev cycles were also reduced.

I was sorry to see it go!

## TECH STACK

- debian linux
- python 3.10+
- apache
- gunicorn
- flask
- mysql
- redis
- phpmyadmin
- webpack
- bootstrap
- vue

## KEY CONCEPTS

- All parameters (whether form or query) get added to the session
- Sessions are "standard" Flask sessions with an extension (Flask-session) for Redis storage
- Carts are not part of the session. Carts will not exist until item(s) are added. They are stored
  in a separate Redis db which persists for a long period of time
- the Cart object is global in the request context (on flask's 'g' variable)

## SECURITY

For XSS protection, I am not sanitizing user input, as it has lead to very mangled strings in the db. Instead, I am relying
on Flask's built-in escaping. See https://flask.palletsprojects.com/en/2.1.x/security/

UPDATE 2022-12-12 - OWASP ZAP proved that flask's built-in escaping for template variables isn't working to stop XSS (OR I am
not using it properly). I modified the templates to use session_safe_get() when printing session variables to html. session_safe_get()
is a wrapper around session_get() but also includes a sanitization feature. TL;DR use session_safe_get() in templates
and / or if you're going to print any data accepted from GET or POST to the html, wrap it in sanitize() or use "{{ data | sanitize }}" filter.

For SQL injection security, I'm using named placeholders (pymysql format). If you need to run a query where parameters won't work, use
F strings and wrap WHERE and AND clause values in DB.esc(), a wrapper method for pymysql's escaping function

# GENERAL TERMS

"variant" - Also known as "option". A size, color, style, etc.
"product" - A base product that appears in the database, has a skuid and a price
"item" - A product that has been fully-configured (all variants chosen), has a quantity,
and is in the cart or on the order. The entire product onbect is
contained in the item in item['product']

# SETUP

Uses docker, BUT you'll also need a python virtualenv in your local project directory. This is so that
the editor is aware of the project and its dependencies. You'll also need direnv installed.

# CONNECTING TO CONTAINERS

Use following command to ssh to containers:

`docker exec -it [CONTAINER NAME] /bin/bash`

For example, to connect to the flaskcommerce-local container:

`docker exec -it flaskcommerce-local /bin/bash`

# TAILING LOGS

You'll probably want to know what the output of the stuff in the containers is, particularly flaskcommerce-local

`docker logs --follow flaskcommerce-local`

# DATABASE CHANGES

If you're making database data or schema changes, please be sure to add them to dev/sql/migrations.sql.

IF you refresh the db from production, you have to run migrations on the container to get your changes back:

mysql -u flaskcommerce -h flaskcommerce-local-database -p flaskcommerce < ./dev-sql/migrations.sql

Also, make sure to occasionally dump the database so it can be added to version control, for collaborative purposes.

From /project dir of flaskcommerce-local container:

`mysqldump -u root -h ${MYSQL_HOST} -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} > dev-sql/01.sql`

If we're in production, schema changes made locally will need to be made on staging and production. That's what migrations.sql is for.

import migrations (after refresh)

`mysql -u root -h flaskcommerce-local-database -p flaskcommerce < ./migrations.sql`

# ADDING NPM PACKAGES

webpack lives outside of docker, so no special docker command needed. Shut down the instance and run this in project directory:

`npm install [PACKAGE]`

# ADDING PYTHON PACKAGES

Not straightforward because the packages live locally in the virtual environment as well as in the container. While the
containers are running, in another terminal do this from project dir (replace [PACKAGE] with name of package you're installing):

`pip3 install [PACKAGE]; pip3 freeze > requirements.txt; docker exec -it flaskcommerce-local pip3 install -r requirements.txt`

unfortunately you have to re-create the container if you want the package there next time you start

# TESTING

for testing flask/python run

`python -m pytest tests/`

from inside the docker container, or this:

`docker exec flaskcommerce-local python -m pytest tests/`

from the host container

# FLASK INTERACTIVE SHELL

for development you can use the flask interactive shell REPL. Unfortunately it does not live-reload when file changes are made.
From WITHIN the docker container:

`flask shell`
`ctx = app.test_request_context()`
`ctx.push()`

Then do imports:

`from flask_app.modules.order import get_order_by_id`

and call functions:

`get_order_by_id("6413266")`
