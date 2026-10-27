from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient

User = get_user_model()


class PatientAPITests(APITestCase):
    def setUp(self):
        # Create two distinct users
        self.user_a = User.objects.create_user(
            email="user_a@example.com",
            name="User A",
            password="StrongPass123!"
        )
        self.user_b = User.objects.create_user(
            email="user_b@example.com",
            name="User B",
            password="StrongPass123!"
        )

        # Create patient owned by User A
        self.patient_a = Patient.objects.create(
            user=self.user_a,
            name="Alice Smith",
            age=30,
            gender="female",
            address="123 Maple Street",
            phone="+12345678901"
        )

        # URLs
        self.list_url = reverse('patient-list')
        self.detail_url_a = reverse('patient-detail', kwargs={'pk': self.patient_a.pk})

    def test_create_patient(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "name": "Bob Brown",
            "age": 45,
            "gender": "male",
            "address": "456 Oak Avenue",
            "phone": "+19876543210"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], "Bob Brown")
        self.assertEqual(response.data['data']['age'], 45)

        # Verify automatic ownership assignment
        created = Patient.objects.get(name="Bob Brown")
        self.assertEqual(created.user, self.user_a)

    def test_create_patient_invalid_data(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "name": "",
            "age": -5,
            "gender": "invalid_gender",
            "address": "",
            "phone": "bad"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('age', response.data)
        self.assertIn('gender', response.data)
        self.assertIn('address', response.data)
        self.assertIn('phone', response.data)

    def test_list_only_authenticated_users_patients(self):
        # Patient owned by User B
        Patient.objects.create(
            user=self.user_b,
            name="Charlie UserB",
            age=50,
            gender="male",
            address="789 Pine Road",
            phone="+1122334455"
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Alice Smith")

    def test_retrieve_owned_patient(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.detail_url_a)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Alice Smith")

    def test_update_owned_patient(self):
        self.client.force_authenticate(user=self.user_a)
        update_data = {
            "name": "Alice Updated",
            "age": 31,
            "gender": "female",
            "address": "Updated Address 99",
            "phone": "+12345678901"
        }
        response = self.client.put(self.detail_url_a, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient_a.refresh_from_db()
        self.assertEqual(self.patient_a.name, "Alice Updated")
        self.assertEqual(self.patient_a.age, 31)

    def test_delete_owned_patient(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(self.detail_url_a)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=self.patient_a.pk).exists())

    def test_prevent_cross_user_patient_access(self):
        # User B should NOT be able to read, update, or delete User A's patient (returns 404)
        self.client.force_authenticate(user=self.user_b)

        # GET User A's patient
        get_response = self.client.get(self.detail_url_a)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        # PUT User A's patient
        put_response = self.client.put(self.detail_url_a, {
            "name": "Hacked",
            "age": 20,
            "gender": "male",
            "address": "Hacked Address",
            "phone": "+1999999999"
        }, format='json')
        self.assertEqual(put_response.status_code, status.HTTP_404_NOT_FOUND)

        # DELETE User A's patient
        delete_response = self.client.delete(self.detail_url_a)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify patient record was not altered or deleted
        self.assertTrue(Patient.objects.filter(pk=self.patient_a.pk).exists())
