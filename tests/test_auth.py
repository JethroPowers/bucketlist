import unittest
import json
from app import create_app, db


class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/auth/register', data=self.user_data)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a success message and a 201 status code
        self.assertEqual(result['message'], "You registered successfully. Please log in.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/auth/register', data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/auth/login', data=not_a_user)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")




"""
- Make sure all your tests pass
- Write tests if they are not existing that prove that a user cannot access a bucketlist without an authorization 
header, and without a proper bearer token, and without a valid token
- Write tests to ensure that proper 401 errors are returned whenever an endpoint is accessed without authorization
- Write tests for login and registration
- Create a new model called bucketlist_item that has items that belong to a particular bucketlist. The table should have
 a foreign key of bucketlist_id that is an id of a bucketlist where it belongs
- Create this route @route(‘/bucketlists/<int:id>/items/’, methods=[‘POST’, ‘GET’]) that accesses all items and adds 
items to a bucketlist. Ensure this route is accessible by authorized users
- Create this route @route(‘/bucketlists/<int:id>/items/<int:item_id>’, methods=[‘GET’, ‘PUT’, ‘DELETE’]) that gets, 
edits and deletes a particular bucketlist item. Ensure this route is accessible by authorized users
- Write all the tests for the bucketlist items routes and code"""
