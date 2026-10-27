import re
from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor CRUD operations with validation.
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    experience_years = serializers.IntegerField(required=True, min_value=0)

    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'email',
            'phone',
            'qualification',
            'experience_years',
            'created_by',
            'created_by_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_email', 'created_at', 'updated_at']

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return stripped

    def validate_specialization(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Specialization cannot be blank.")
        return stripped

    def validate_qualification(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Qualification cannot be blank.")
        return stripped

    def validate_email(self, value):
        normalized = value.strip().lower()
        if not normalized:
            raise serializers.ValidationError("Email cannot be blank.")
        # Check uniqueness during creation or updating different doctor
        query = Doctor.objects.filter(email=normalized)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this email address already exists.")
        return normalized

    def validate_phone(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Phone number cannot be blank.")
        pattern = r'^\+?[0-9\s\-]{7,20}$'
        if not re.match(pattern, stripped):
            raise serializers.ValidationError(
                "Phone number is invalid. Must contain 7 to 20 digits, optionally prefixed with '+'."
            )
        return stripped

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience years cannot be negative.")
        return value
