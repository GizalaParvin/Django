from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Doctor(models.Model):
    """
    Doctor model representing medical professionals directory.
    Visible to all authenticated users, but mutable only by creator.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_doctors',
        help_text="User who added this doctor profile."
    )
    name = models.CharField(max_length=255, help_text="Doctor's full name.")
    specialization = models.CharField(max_length=255, help_text="Medical specialty.")
    email = models.EmailField(unique=True, help_text="Doctor's unique email address.")
    phone = models.CharField(max_length=20, help_text="Contact phone number.")
    qualification = models.CharField(max_length=255, help_text="Academic and medical degrees.")
    experience_years = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Non-negative integer representing years of clinical experience."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'doctor'
        verbose_name_plural = 'doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization} ({self.experience_years} yrs exp)"
