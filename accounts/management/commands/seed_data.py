from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with demo users, doctors, patients, and mappings for testing."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding healthcare database...")

        # 1. Create Demo Users
        admin_user, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={"name": "System Administrator", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("Admin1234!")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        demo_user, _ = User.objects.get_or_create(
            email="demo@example.com",
            defaults={"name": "Demo User"}
        )
        demo_user.set_password("DemoPass123!")
        demo_user.save()

        self.stdout.write(self.style.SUCCESS(f"Users created: {admin_user.email}, {demo_user.email}"))

        # 2. Create Doctors
        doctor_data = [
            {
                "name": "Rajesh Verma",
                "specialization": "Cardiology",
                "email": "dr.rajesh@example.com",
                "phone": "+919811223344",
                "qualification": "MBBS, MD (Cardiology)",
                "experience_years": 15,
                "created_by": demo_user,
            },
            {
                "name": "Priya Nair",
                "specialization": "Neurology",
                "email": "dr.priya@example.com",
                "phone": "+919822334455",
                "qualification": "MBBS, DM (Neurology)",
                "experience_years": 12,
                "created_by": demo_user,
            },
            {
                "name": "Vikram Sethi",
                "specialization": "Pediatrics",
                "email": "dr.vikram@example.com",
                "phone": "+919833445566",
                "qualification": "MBBS, DCH, MD (Pediatrics)",
                "experience_years": 9,
                "created_by": demo_user,
            },
        ]

        doctors = []
        for d in doctor_data:
            doc, _ = Doctor.objects.get_or_create(email=d["email"], defaults=d)
            doctors.append(doc)

        self.stdout.write(self.style.SUCCESS(f"Created {len(doctors)} doctors."))

        # 3. Create Patients
        patient_data = [
            {
                "user": demo_user,
                "name": "Riya Sharma",
                "age": 28,
                "gender": "female",
                "address": "42 Park Avenue, New Delhi",
                "phone": "+919876543210",
            },
            {
                "user": demo_user,
                "name": "Amit Kumar",
                "age": 45,
                "gender": "male",
                "address": "12 Civil Lines, Jaipur",
                "phone": "+919876543211",
            },
        ]

        patients = []
        for p in patient_data:
            pat, _ = Patient.objects.get_or_create(
                user=p["user"],
                name=p["name"],
                defaults=p
            )
            patients.append(pat)

        self.stdout.write(self.style.SUCCESS(f"Created {len(patients)} patients."))

        # 4. Create Mappings
        m1, _ = PatientDoctorMapping.objects.get_or_create(
            patient=patients[0],
            doctor=doctors[0]
        )
        m2, _ = PatientDoctorMapping.objects.get_or_create(
            patient=patients[0],
            doctor=doctors[1]
        )

        self.stdout.write(self.style.SUCCESS("Assigned doctors to patients."))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
