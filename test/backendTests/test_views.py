from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import RequestFactory
from unittest.mock import patch, ANY
from api.views import google_id
from api.models import Matches
from django.contrib.sessions.middleware import SessionMiddleware
import json

test_email = 'testuser@example.com'
application_json = 'application/json'

class RegisterViewTest(TestCase):
    def setUp(self):
        self.test_user_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'test@gmail.com',
        }

        self.client = Client()

    def test_register_view_post(self):
        # Simulate a POST request to the register view
        response = self.client.post(reverse('register'), data=self.test_user_data)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the user was created successfully
        self.assertEqual(User.objects.filter(username='testuser').exists(), True)

    def test_register_view_invalid_data(self):
        

        # Simulate a POST request to the register view with invalid data
        response = self.client.post(reverse('register'), data={'username': 'invalid'})

        # Check if the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content contains the error message
        self.assertIn('This field is required', response.content.decode())

    def test_register_view_invalid_method(self):
        

        # Simulate a GET request to the register view
        response = self.client.get(reverse('register'))

        # Check if the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content contains the error message
        self.assertIn('Invalid request method!', response.content.decode())


class UserLoginTestCase(TestCase):
    def setUp(self):

        self.user_email = test_email
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email=self.user_email,
            password='testpassword'
        )

        # URL for the userLogin view
        self.login_url = reverse('login')
        self.client = Client()

    def test_user_login_logout(self):
        # Data to be sent in the POST request
        data = {
            'email': self.user_email,
            'password': 'testpassword',
        }

        logged_in = self.client.get(reverse('check_login')).json()
        self.assertEqual(logged_in['loggedIn'], False)

        # Send a POST request to the userLogin view
        response = self.client.post(self.login_url, data)

        # Check if the response is successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response content is as expected
        self.assertEqual(response.content, b'User logged in successfully!')

        logged_in = self.client.get(reverse('check_login')).json()
        self.assertEqual(logged_in['loggedIn'], True)

    def test_user_login_invalid_credentials(self):
        # Data with invalid credentials
        data = {
            'email': self.user_email,
            'password': 'wrongpassword',
        }

        # Send a POST request to the userLogin view
        response = self.client.post(self.login_url, data)

        # Check if the response is a bad request (HTTP 400 Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content is as expected
        self.assertEqual(response.content, b'Invalid email or password!')

    def test_user_login_invalid_method(self):
        # Send a GET request to the userLogin view (invalid method)
        response = self.client.get(self.login_url)

        # Check if the response is a bad request (HTTP 400 Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content is as expected
        self.assertEqual(response.content, b'Invalid request method!')


class GoogleLoginTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client_id = '613529435942-nfjfd37rhd01pbqjrkg8tfqa0uvdildg.apps.googleusercontent.com'
        self.user_email = test_email
        self.username = 'testuser'  # Assume generate_username works correctly
        self.id_token_string = 'mock_id_token'
        self.middleware = SessionMiddleware(lambda request: None)
        self.client = Client()
        self.token = 'api.views.id_token.verify_oauth2_token'
        self.login_url = reverse('googleID')

    def add_session(self, request):
        self.middleware.process_request(request)
        request.session.save()

    @patch('api.views.id_token.verify_oauth2_token')
    def test_google_oauth2_service(self, mock_verify):
        mock_verify.return_value = {'email': self.user_email}
        request = self.factory.post(self.login_url, json.dumps({'id_token': self.id_token_string}), content_type=application_json)
        self.add_session(request)
        response = google_id(request)
        self.assertEqual(response.status_code, 200)
        mock_verify.assert_called_once_with(self.id_token_string, ANY, self.client_id)

    def test_user_creation(self):
        request = self.factory.post(self.login_url, json.dumps({'id_token': self.id_token_string}), content_type=application_json)
        self.add_session(request)
        with patch(self.token, return_value={'email': self.user_email}):
            response = google_id(request)
            self.assertEqual(response.status_code, 200)
            user = User.objects.get(email=self.user_email)
            self.assertEqual(user.username, self.username)

    def test_existing_user_login(self):
        User.objects.create(email=self.user_email, username=self.username)
        request = self.factory.post(self.login_url, json.dumps({'id_token': self.id_token_string}), content_type=application_json)
        self.add_session(request)
        with patch(self.token, return_value={'email': self.user_email}):
            response = google_id(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects.count(), 1)  # No new user should be created

    def test_invalid_token(self):
        request = self.factory.post(self.login_url, json.dumps({'id_token': 'invalid_token'}), content_type=application_json)
        self.add_session(request)
        with patch(self.token, side_effect=ValueError('Invalid Token')):
            response = google_id(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), {'success': False, 'error': 'Invalid Token'})

class DBViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_email = test_email

        # Create a test user
        User.objects.create_user(
            username='testuser',
            email=self.user_email,
            password='testpassword'
        )
        
    def test_player_loc_stats(self):
        response = self.client.get(reverse('player_loc_stats', args=['testuser']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'player_name': 'testuser', 'n_wins': 0, 'n_lost': 0, 'n_draws': 0, 'elo': 1440})

    def test_player_username(self):
        response = self.client.get(reverse('player_username', args=[self.user_email]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'username': 'testuser'})

    def test_leaderboard(self):
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'leaderboard': [{'player_name': 'testuser', 'n_wins': 0, 'n_draws': 0, 'n_lost': 0, 'elo': 1440}]})

    def test_search_room_fail(self):
        response = self.client.get(reverse('rooms', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'Room not found!')

    def test_search_room_success(self):
        #create a room
        Matches.objects.create(room_name='game_room', player1='testuser', player2='testuser', finished=False)

        response = self.client.get(reverse('rooms', args=['room']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Room found!')