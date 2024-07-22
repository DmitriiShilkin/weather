from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import History, City
from sign.models import CustomUser


class GetWeatherTest(TestCase):

    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.history_url = reverse('history')
        self.index_url = reverse('index')

        self.user1 = CustomUser.objects.create_user(
            email='testmail@gmail.com',
            username='test_username',
            first_name='User first name',
            last_name='User last name',
            password='JiqY7whfay'
        )
        view_history_permission = Permission.objects.get(codename='view_history')
        self.user1.user_permissions.add(view_history_permission)

        self.user2 = CustomUser.objects.create_user(
            email='testmail2@gmail.com',
            username='test_username2',
            first_name='User first name',
            last_name='User last name',
            password='JiqY7whfay'
        )

        self.city1 = City.objects.create(
            name='Test name 1',
            name_ascii='Test name ascii 1',
            latitude=35.6897,
            longitude=139.6922,
            country='Test country 1',
            iso2='TC',
            iso3='TCO',
            region='Test region 1',
            population=37732000
        )

        self.city2 = City.objects.create(
            name='Test name 2',
            name_ascii='Test name ascii 2',
            latitude=-6.1750,
            longitude=106.8275,
            country='Test country 2',
            iso2='T2',
            iso3='TC2',
            region='Test region 2',
            population=33756000
        )

        self.history1 = History.objects.create(
            city=self.city1,
            user=self.user1
        )

        self.history2 = History.objects.create(
            city=self.city2,
            user=self.user1
        )
        self.history3 = History.objects.create(
            city=self.city2,
            user=self.user2
        )

    def test_can_register(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign/signup.html')

    def test_can_login(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign/login.html')

    def test_get_history_list(self):
        login = self.client.login(email='testmail@gmail.com', password='JiqY7whfay')
        self.assertEqual(login, True)
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'], 'test_username')
        self.assertEqual(len(response.context['cities']), 2)

    def test_get_history_list_unauthorized(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 403)

    def test_repeat_get_weather(self):
        last_viewed = History.objects.filter(user_id=self.user1).last()
        login = self.client.login(email='testmail@gmail.com', password='JiqY7whfay')
        self.assertEqual(login, True)
        response = self.client.get(f'/repeat/{last_viewed}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'], 'test_username')
        self.assertEqual(response.context['city'], last_viewed.city)

    def test_post_valid_city(self):
        post_data = {
            'city_name': "('Test name ascii 1', 'Test country 1', 'Test region 1')"
        }
        login = self.client.login(email='testmail@gmail.com', password='JiqY7whfay')
        self.assertEqual(login, True)
        response = self.client.post(self.index_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(response.context['city'], self.city1)
        self.assertTrue(response.context['user'], 'test_username')
        self.assertIn('result', response.context)
        self.assertIn('cities_names', response.context)
        self.assertTrue(History.objects.filter(city=self.city1, user=self.user1).exists())

    def test_post_invalid_city(self):
        post_data = {
            'city_name': "('NonExistentCity', 'NonExistentCountry', 'NonExistentRegion')"
        }
        response = self.client.post(self.index_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'city/invalid_name.html')
        self.assertNotIn('city', response.context)
        self.assertNotIn('result', response.context)

    def test_post_invalid_syntax(self):
        post_data = {
            'city_name': "Invalid City String"
        }
        response = self.client.post(self.index_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'city/invalid_name.html')
        self.assertNotIn('city', response.context)
        self.assertNotIn('result', response.context)
