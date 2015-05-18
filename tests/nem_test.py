import unittest
from penn import News, Map
import json


class TestNEM(unittest.TestCase):

    def setUp(self):
        from credentials import NEM_USERNAME, NEM_PASSWORD
        username = NEM_USERNAME
        password = NEM_PASSWORD
        self.assertFalse(username is None or password is None)
        self.news = News(username, password)
        self.map = Map(username, password)

    def test_news(self):
        data = self.news.search("pennsylvania")
        self.assertEquals(data['result_data'][0]['content_type'], 'news')


    def test_map(self):
        data = self.map.search("Towne")
        self.assertEquals(data['result_data'][0]['content_type'], 'map')