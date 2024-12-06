def test_email_opt(app, client):

    """Test email subscription"""
    with app.test_request_context():
        from flask_app.modules.extensions import DB
        from flask_app.modules.helpers import get_random_string

        fake_email = get_random_string() + "@testemail.com"

        # send request, assert that the endpoint sends back its strange success response
        response = client.post(
            "/process_email_capture",
            data={"bill_email": fake_email, "request": "optinrequest", "optin": "yes", "capture": "Y"},
        )
        assert response.json[0]["result"] == "0"

        # check that the email exists in the db and is opted in
        res = DB.fetch_one("SELECT optin FROM customers WHERE bill_email = %(fake_email)s", {"fake_email": fake_email})
        assert res.get("optin") == "yes"

        # test opt out request
        response = client.post(
            "/api/optchange",
            data={"bill_email": fake_email, "request": "optoutrequest", "optin": "no"},
            follow_redirects=True,
        )
        assert response.json["success"] == True

        # check that the email exists in the db and is opted in
        res = DB.fetch_one(
            "SELECT customer_id, optin FROM customers WHERE bill_email = %(fake_email)s", {"fake_email": fake_email}
        )
        assert res.get("optin") == "no"

        # clean up
        deleted = DB.delete_query(
            "DELETE FROM customers WHERE customer_id = %(customer_id)s", {"customer_id": res.get("customer_id")}
        )
        assert deleted == 1
