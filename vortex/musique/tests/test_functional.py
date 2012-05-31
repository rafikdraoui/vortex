from selenium import webdriver
from django.test import LiveServerTestCase


#TODO
class SimpleTest(LiveServerTestCase):
    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)
