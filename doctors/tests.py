from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from doctors.models import Doctor

User = get_user_model()


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="doctor_admin_a@example.com",
            name="Admin User A",
            password="StrongPass123!"
        )
        self.user_b = User.objects.create_user(
            email="doctor_admin_b@example.com",
            name="Admin User B",
            password="StrongPass123!"
        )

        self.doctor_a = Doctor.objects.create(
            created_by=self.user_a,
            name="Gregory House",
            specialization="Diagnostic Medicine",
            email="dr.house@example.com",
            phone="+1234567890",
            qualification="MD, Board Certified",
            experience_years=20
        )

        self.list_url = reverse('doctor-list')
        self.detail_url_a = reverse('doctor-detail', kwargs={'pk': self.doctor_a.pk})

    def test_create_doctor(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "name": "Allison Cameron",
            "specialization": "Immunology",
            "email": "dr.cameron@example.com",
            "phone": "+1987654321",
            "qualification": "MD",
            "experience_years": 8
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], "Allison Cameron")

        doctor = Doctor.objects.get(email="dr.cameron@example.com")
        self.assertEqual(doctor.created_by, self.user_a)

    def test_list_doctors_visible_to_all_authenticated_users(self):
        # User B should be able to view the doctor directory (including doctors created by User A)
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertGreaterEqual(len(results), 1)
        emails = [d['email'] for d in results]
        self.assertIn("dr.house@example.com", emails)

    def test_retrieve_doctor_visible_to_all_authenticated_users(self):
        # User B retrieves doctor created by User A
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.detail_url_a)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Gregory House")

    def test_update_doctor_by_creator(self):
        self.client.force_authenticate(user=self.user_a)
        update_data = {
            "name": "Gregory House, M.D.",
            "specialization": "Diagnostic Medicine & Nephrology",
            "email": "dr.house@example.com",
            "phone": "+1234567890",
            "qualification": "MD, Head of Diagnostics",
            "experience_years": 22
        }
        response = self.client.put(self.detail_url_a, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor_a.refresh_from_db()
        self.assertEqual(self.doctor_a.experience_years, 22)

    def test_delete_doctor_by_creator(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(self.detail_url_a)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=self.doctor_a.pk).exists())

    def test_prevent_non_creator_from_modifying_or_deleting_doctor(self):
        # User B attempts to modify doctor created by User A -> Must return 404
        self.client.force_authenticate(user=self.user_b)

        put_response = self.client.put(self.detail_url_a, {
            "name": "Malicious Modification",
            "specialization": "Unknown",
            "email": "dr.house@example.com",
            "phone": "+1234567890",
            "qualification": "None",
            "experience_years": 0
        }, format='json')
        self.assertEqual(put_response.status_code, status.HTTP_404_NOT_FOUND)

        delete_response = self.client.delete(self.detail_url_a)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)

        # Confirm doctor remains unchanged
        self.doctor_a.refresh_from_db()
        self.assertEqual(self.doctor_a.name, "Gregory House")
