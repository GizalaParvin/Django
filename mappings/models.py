from django.db import models
from patients.models import Patient
from doctors.models import Doctor


class PatientDoctorMapping(models.Model):
    """
    Model associating patients with assigned doctors.
    Enforces uniqueness so a doctor cannot be assigned to the same patient multiple times.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text="The patient being assigned a doctor."
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text="The doctor assigned to the patient."
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'patient doctor mapping'
        verbose_name_plural = 'patient doctor mappings'
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'doctor'],
                name='unique_patient_doctor_assignment'
            )
        ]

    def __str__(self):
        return f"{self.patient.name} -> Dr. {self.doctor.name}"
