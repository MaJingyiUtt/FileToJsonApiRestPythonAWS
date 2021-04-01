"""This module is for pytest of app.py"""
import unittest

import app


class TestMethods(unittest.TestCase):
    """This class is for unit test"""

    def test_upload_txt(self):
        """Tests if post  works well"""
        file = "test.txt"
        data = {"file": (open(file, "rb"), file)}
        with app.app.test_client() as test_client:
            response = test_client.post("/upload", data=data)
            self.assertEqual(response.status_code, 200)
