from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')
        self.patients_url = reverse('patient-list')

        self.user_data = {
            "name": "Aman Sharma",
            "email": "aman@example.com",
            "password": "StrongPassword123!"
        }
        self.existing_user = User.objects.create_user(
            email="existing@example.com",
            name="Existing User",
            password="StrongPassword123!"
        )

    def test_successful_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('message'), "User registered successfully.")
        
        user_info = response.data.get('data', {})
        self.assertEqual(user_info.get('email'), self.user_data['email'])
        self.assertEqual(user_info.get('name'), self.user_data['name'])
        self.assertNotIn('password', user_info)

        user = User.objects.get(email=self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_duplicate_email_registration(self):
        data = {
            "name": "Another Aman",
            "email": "existing@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_invalid_email_registration(self):
        data = {
            "name": "Invalid Email User",
            "email": "not-an-email",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_weak_or_short_password_registration(self):
        data = {
            "name": "Weak Pass User",
            "email": "weak@example.com",
            "password": "123"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_successful_login(self):
        credentials = {
            "email": "existing@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotIn('password', response.data)

    def test_login_with_incorrect_password(self):
        credentials = {
            "email": "existing@example.com",
            "password": "WrongPassword999!"
        }
        response = self.client.post(self.login_url, credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_without_token(self):
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_endpoint(self):
        # First login to obtain valid refresh token
        login_res = self.client.post(self.login_url, {
            "email": "existing@example.com",
            "password": "StrongPassword123!"
        }, format='json')
        refresh_token = login_res.data['refresh']

        # Refresh the token
        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_refresh_token(self):
        response = self.client.post(self.refresh_url, {"refresh": "invalid_token_string"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
