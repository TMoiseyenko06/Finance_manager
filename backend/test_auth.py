import unittest
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock, patch
import mongomock


class testAuth(unittest.TestCase):
    def setUp(self):
        
        self.mock_db_client = mongomock.MongoClient()
        self.mock_db = self.mock_db_client.finance_db
        patch('pymongo.MongoClient', return_value=self.mock_db_client).start()
        patch('database.db', self.mock_db).start()
        from app import app
        patch('utils.util.verify_token', return_value = None).start()
        self.app = app.test_client()

    def tearDown(self):
        patch.stopall()

    def test_register(self):
        payload = {
            "username":"test",
            "password":"test"
        }
        self.mock_db.accounts = []
        response = self.app.post('/auth/register',json=payload)
        self.assertEqual(response.status_code,201)

    def test_login(self):
        payload = {
            "username":"tests",
            "password":"tests"
        }
        self.mock_db.accounts.insert_one({
            "username": "tests", 
            "password": generate_password_hash("tests")
        })
        response = self.app.get('/auth/login',json=payload)
        self.assertEqual(response.status_code,200)

if __name__ == '__main__':
    unittest.main()