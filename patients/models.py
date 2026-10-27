from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Patient(models.Model):
    """
    Patient model representing health records owned by a registered user.
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        help_text="Authenticated user who owns this patient record."
    )
    name = models.CharField(max_length=255, help_text="Patient's full name.")
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(150)],
        help_text="Positive integer representing patient's age in years."
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Gender selection: male, female, or other."
    )
    address = models.TextField(help_text="Patient's residential address.")
    phone = models.CharField(max_length=20, help_text="Contact telephone or mobile number.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'patient'
        verbose_name_plural = 'patients'

    def __str__(self):
        return f"{self.name} (Age: {self.age}, ID: {self.id})"
