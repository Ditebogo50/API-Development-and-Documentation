import os
import unittest
import json

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf"
        self.database_path = "postgresql://{}:{}@{}/{}".format("student", "student", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        #new book onject
        self.new_book = {
            "title": "Anansi Boys", 
            "author": "Neil Gaiman", 
            "rating": 5
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_books(self):
        #get the endpoint
        res = self.client().get("/books")
        #load the data using json.loads
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/books?page=1000", json={"rating": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
#search book
    def test_get_book_search_with_results(self):
        res = self.client().post("/books", json={"search": "Novel"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        #length of books with novel
        self.assertEqual(len(data["books"]), 4)

    def test_get_book_search_without_results(self):
        #use a term not available in database
        res = self.client().post("/books", json={"search": "applejacks"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_books"], 0)
        self.assertEqual(len(data["books"]), 0)   
#update
    def test_update_book_rating(self):
        res = self.client().patch("/books/5", json={"rating": 1})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        #check in db if the rating is changed to 1
        self.assertEqual(book.format()["rating"], 1)

    #if we dont provide any rating info we get 400
    def test_400_for_failed_update(self):
        #missing that json body
        res = self.client().patch("/books/5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")
#post end points
    def test_create_new_book(self):
        #send json of the object we created during that setup
        res = self.client().post("/books", json=self.new_book)
        #data of the response
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["books"]))

    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post("/books/45", json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    # Delete a different book in each attempt
    def test_delete_book(self):
        res = self.client().delete("/books/2")
        data = json.loads(res.data)

        book = Book.query.filter(Book.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))
        self.assertEqual(book, None)

    def test_422_if_book_does_not_exist(self):
        res = self.client().delete("/books/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()