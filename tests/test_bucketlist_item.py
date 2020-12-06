import unittest
import os
import json
from app import create_app, db

class BucketlistItemTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go to Borabora for vacation'}
        self.bucketlist_item = {'name': 'Book flight to Borabora'}

        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_bucketlist_item_creation(self):
        """Test API can create a bucketlist item (POST request)"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        res = self.client().post('/auth/register', data=self.user_data)
        buc = self.client().post('/bucketlists/', data=self.bucketlist)
        buc_json = json.loads(buc.data)
        buc_id = buc_json['id']
        print(buc_id)
        res = self.client().post(f'/bucketlists//items/', data=self.bucketlist_item)
        self.assertEqual(res.status_code, 201)
        # self.assertIn('Go to Borabora', str(res.data))
        buxketlist = json.loads(res.data)
        self.assertEqual(self.bucketlist['name'], buxketlist['name'])

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()