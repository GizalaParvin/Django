import re
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient CRUD operations with field-level validations.
    """
    phone = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'address',
            'phone',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Name cannot be blank.")
        return stripped

    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be a positive integer greater than 0.")
        if value > 150:
            raise serializers.ValidationError("Age cannot exceed 150.")
        return value

    def validate_gender(self, value):
        valid_genders = [choice[0] for choice in Patient.GENDER_CHOICES]
        normalized = value.strip().lower()
        if normalized not in valid_genders:
            raise serializers.ValidationError(
                f"Invalid gender choice '{value}'. Choose from: {', '.join(valid_genders)}."
            )
        return normalized

    def validate_address(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Address cannot be blank.")
        return stripped

    def validate_phone(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Phone number cannot be blank.")
        # Allow numbers, optional leading +, optional dashes/spaces, length 7-20
        pattern = r'^\+?[0-9\s\-]{7,20}$'
        if not re.match(pattern, stripped):
            raise serializers.ValidationError(
                "Phone number is invalid. Must contain 7 to 20 digits, optionally prefixed with '+'."
            )
        return stripped
