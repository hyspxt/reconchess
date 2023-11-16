from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTest(TestCase):
    def setUp(self):
        self.test_user_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'test@gmail.com',
        }

    def test_register_view_post(self):
        client = Client()

        # Simulate a POST request to the register view
        response = client.post(reverse('register'), data=self.test_user_data)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the user was created successfully
        self.assertEqual(User.objects.filter(username='testuser').exists(), True)

    def test_register_view_invalid_data(self):
        client = Client()

        # Simulate a POST request to the register view with invalid data
        response = client.post(reverse('register'), data={'username': 'invalid'})

        # Check if the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content contains the error message
        self.assertIn('This field is required', response.content.decode())

    def test_register_view_invalid_method(self):
        client = Client()

        # Simulate a GET request to the register view
        response = client.get(reverse('register'))

        # Check if the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Check if the response content contains the error message
        self.assertIn('Invalid request method!', response.content.decode())


class UserLoginTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        # URL for the userLogin view
        self.login_url = reverse('login')

    def test_user_login_successful(self):
        # Data to be sent in the POST request
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }

        # Send a POST request to the userLogin view
        response = self.client.post(self.login_url, data)

        # Check if the response is successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response content is as expected
        self.assertEqual(response.content, b'User logged in successfully!')

    def test_user_login_invalid_credentials(self):
        # Data with invalid credentials
        data = {
            'email': 'testuser@example.com',
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

    