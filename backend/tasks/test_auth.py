"""Unit tests for registration, login and logout (token authentication)."""
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = '/api/register/'
LOGIN_URL = '/api/login/'
LOGOUT_URL = '/api/logout/'
TASKS_URL = '/api/tasks/'


class RegisterTests(APITestCase):
    def test_register_creates_user_and_returns_token(self):
        response = self.client.post(
            REGISTER_URL, {'username': 'alice', 'password': 'Testpass123!'}, format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'alice')
        self.assertTrue(User.objects.filter(username='alice').exists())

    def test_register_rejects_short_password(self):
        response = self.client.post(
            REGISTER_URL, {'username': 'bob', 'password': 'short'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='bob').exists())

    def test_register_rejects_missing_username(self):
        response = self.client.post(
            REGISTER_URL, {'username': '', 'password': 'Testpass123!'}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(username='alice', password='Testpass123!')
        response = self.client.post(
            REGISTER_URL, {'username': 'alice', 'password': 'Another123!'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username='alice').count(), 1)


class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='alice', password='Testpass123!')

    def test_login_with_valid_credentials_returns_token(self):
        response = self.client.post(
            LOGIN_URL, {'username': 'alice', 'password': 'Testpass123!'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'alice')

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            LOGIN_URL, {'username': 'alice', 'password': 'wrong-password'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)

    def test_login_with_unknown_user_fails(self):
        response = self.client.post(
            LOGIN_URL, {'username': 'nobody', 'password': 'Testpass123!'}, format='json'
        )
        self.assertEqual(response.status_code, 400)


class LogoutAndAccessTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='Testpass123!')
        self.token = Token.objects.create(user=self.user)

    def test_tasks_require_authentication(self):
        self.assertEqual(self.client.get(TASKS_URL).status_code, 401)

    def test_valid_token_grants_access(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(self.client.get(TASKS_URL).status_code, 200)

    def test_logout_deletes_token_and_blocks_further_access(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(self.client.post(LOGOUT_URL).status_code, 204)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        # The old token must no longer work.
        self.assertEqual(self.client.get(TASKS_URL).status_code, 401)

    def test_logout_requires_authentication(self):
        self.assertEqual(self.client.post(LOGOUT_URL).status_code, 401)
