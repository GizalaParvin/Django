from rest_framework import serializers
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping


class DoctorSummarySerializer(serializers.ModelSerializer):
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
        ]


class PatientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'gender', 'phone']


class PatientDoctorMappingReadSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    doctor = DoctorSummarySerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'assigned_at']


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        required=True,
        help_text="ID of the patient owned by the authenticated user."
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        required=True,
        help_text="ID of the doctor to be assigned."
    )

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Authorization: user must own the patient
        if user and patient.user != user:
            raise serializers.ValidationError(
                {"patient": "You can only assign doctors to patients that you own."}
            )

        # Uniqueness check: avoid duplicate assignments
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {"detail": "This doctor is already assigned to this patient."}
            )

        return attrs

    def to_representation(self, instance):
        # Return rich response with nested patient and doctor details
        return PatientDoctorMappingReadSerializer(instance, context=self.context).data
