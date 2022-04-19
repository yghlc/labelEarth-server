from django.test import TestCase

# run "python manage.py test imageObjects" for test

from .views import getItemOfImageObject_user

# Create your tests here for the internal behavior of the code.
class imageObjectsTests(TestCase):
    def test_helloworld(self):
        print('This is the test!')

# Creat tests for a view.
from django.test.utils import teardown_test_environment, setup_test_environment
try:
    # If setup_test_environment haven't been called previously this
    # will produce an AttributeError.
    teardown_test_environment()
except AttributeError:
    pass
setup_test_environment()

from django.test import Client
client = Client()

from django.urls import reverse

class imageObjectsViewTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))        # imageObject:index  (should omit imageObject)
        self.assertEqual(response.status_code, 200)

    def test_getItemOfImageObject(self):
        response = self.client.get(reverse('getItemOfImageObject'))
        self.assertEqual(response.status_code, 200)

    def test_getItemOfImageObject_user(self):
        user_name = 'huanglingcao'
        # # url to get an item for a user (huanglingcao is the username)
        # http://127.0.0.1:8000/imageObjects/huanglingcao/getitem
        url = reverse('getItemOfImageObject_user',args={user_name})
        print('\n','reverse URL: ',url,'\n')
        response = self.client.get(url)

        ## test faild: django.contrib.auth.models.User.DoesNotExist: User matching query does not exist.
        ## but put the url in browser, it works fine.
        self.assertEqual(response.status_code, 200)

