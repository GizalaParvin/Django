from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="mapping_user_a@example.com",
            name="User A",
            password="StrongPass123!"
        )
        self.user_b = User.objects.create_user(
            email="mapping_user_b@example.com",
            name="User B",
            password="StrongPass123!"
        )

        self.patient_a = Patient.objects.create(
            user=self.user_a,
            name="Patient A",
            age=25,
            gender="female",
            address="Street 1",
            phone="+1234567890"
        )
        self.patient_b = Patient.objects.create(
            user=self.user_b,
            name="Patient B",
            age=40,
            gender="male",
            address="Street 2",
            phone="+1234567899"
        )

        self.doctor_1 = Doctor.objects.create(
            created_by=self.user_a,
            name="Doctor One",
            specialization="Cardiology",
            email="doc1@example.com",
            phone="+1987654321",
            qualification="MD",
            experience_years=10
        )
        self.doctor_2 = Doctor.objects.create(
            created_by=self.user_b,
            name="Doctor Two",
            specialization="Neurology",
            email="doc2@example.com",
            phone="+1987654322",
            qualification="MD, PhD",
            experience_years=15
        )

        self.mapping_list_url = reverse('mapping-list-create')

    def test_assign_doctor_to_owned_patient(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "patient": self.patient_a.id,
            "doctor": self.doctor_1.id
        }
        response = self.client.post(self.mapping_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Doctor assigned to patient successfully.")
        self.assertEqual(response.data['data']['doctor']['name'], "Doctor One")
        self.assertEqual(response.data['data']['patient']['name'], "Patient A")

        self.assertTrue(
            PatientDoctorMapping.objects.filter(
                patient=self.patient_a,
                doctor=self.doctor_1
            ).exists()
        )

    def test_reject_assigning_doctor_to_another_users_patient(self):
        # User A tries to assign doctor to User B's patient
        self.client.force_authenticate(user=self.user_a)
        data = {
            "patient": self.patient_b.id,
            "doctor": self.doctor_1.id
        }
        response = self.client.post(self.mapping_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)

    def test_reject_duplicate_assignment(self):
        # Create initial assignment
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1
        )

        self.client.force_authenticate(user=self.user_a)
        data = {
            "patient": self.patient_a.id,
            "doctor": self.doctor_1.id
        }
        response = self.client.post(self.mapping_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_current_users_mappings(self):
        # Mapping for User A
        mapping_a = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1
        )
        # Mapping for User B
        mapping_b = PatientDoctorMapping.objects.create(
            patient=self.patient_b,
            doctor=self.doctor_2
        )

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.mapping_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], mapping_a.id)
        self.assertEqual(results[0]['patient']['id'], self.patient_a.id)

    def test_list_doctors_assigned_to_specific_patient(self):
        # Assign two doctors to patient_a
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_2
        )

        patient_mapping_url = reverse(
            'mapping-detail-or-patient',
            kwargs={'pk': self.patient_a.id}
        )
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(patient_mapping_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        doctor_names = [m['doctor']['name'] for m in response.data]
        self.assertIn("Doctor One", doctor_names)
        self.assertIn("Doctor Two", doctor_names)

    def test_prevent_cross_user_patient_mapping_inspection(self):
        # User B attempts to inspect mappings for User A's patient -> Must return 404
        patient_mapping_url = reverse(
            'mapping-detail-or-patient',
            kwargs={'pk': self.patient_a.id}
        )
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(patient_mapping_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_authorized_mapping(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1
        )
        delete_url = reverse('mapping-detail-or-patient', kwargs={'pk': mapping.id})

        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping.id).exists())

    def test_prevent_cross_user_mapping_deletion(self):
        # User B attempts to delete User A's mapping -> Must return 404
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1
        )
        delete_url = reverse('mapping-detail-or-patient', kwargs={'pk': mapping.id})

        self.client.force_authenticate(user=self.user_b)
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=mapping.id).exists())
