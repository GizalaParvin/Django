from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import (
    PatientDoctorMappingReadSerializer,
    PatientDoctorMappingCreateSerializer,
)


class MappingListCreateView(generics.ListCreateAPIView):
    """
    GET /api/mappings/
    List all doctor-patient mappings belonging to the authenticated user's patients.

    POST /api/mappings/
    Assign a doctor to a patient owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientDoctorMappingCreateSerializer
        return PatientDoctorMappingReadSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PatientDoctorMapping.objects.none()
        return (
            PatientDoctorMapping.objects
            .filter(patient__user=self.request.user)
            .select_related('patient', 'doctor')
            .order_by('-assigned_at')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        read_serializer = PatientDoctorMappingReadSerializer(instance)
        return Response(
            {
                "message": "Doctor assigned to patient successfully.",
                "data": read_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class MappingDetailOrPatientView(APIView):
    """
    Handles:
    - GET /api/mappings/<patient_id>/
      List all doctors assigned to a specific patient owned by the authenticated user.
      Returns HTTP 404 if patient is not found or not owned by the requesting user.

    - DELETE /api/mappings/<id>/
      Remove a specific doctor assignment by mapping ID.
      Returns HTTP 404 if mapping is not found or not owned by the requesting user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # Validate that the patient exists and belongs to the authenticated user
        patient = get_object_or_404(Patient, pk=pk, user=request.user)
        mappings = (
            PatientDoctorMapping.objects
            .filter(patient=patient)
            .select_related('doctor', 'patient')
            .order_by('-assigned_at')
        )
        serializer = PatientDoctorMappingReadSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        # Validate that the mapping exists and is linked to a patient owned by requesting user
        mapping = get_object_or_404(
            PatientDoctorMapping,
            pk=pk,
            patient__user=request.user
        )
        mapping.delete()
        return Response(
            {"message": "Doctor assignment removed successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
