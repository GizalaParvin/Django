from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient records.
    Only allows access to patient records owned by the authenticated user.
    """
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Strictly scope records to the authenticated requesting user
        if not self.request.user.is_authenticated:
            return Patient.objects.none()

        queryset = Patient.objects.filter(user=self.request.user).order_by('-created_at')

        # Filter by gender
        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender.strip().lower())

        # Search by name or phone
        search = self.request.query_params.get('search')
        if search:
            query = search.strip()
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(phone__icontains=query)
            )

        return queryset

    def perform_create(self, serializer):
        # Automatically assign ownership to the authenticated user
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Patient created successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "message": "Patient updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Patient deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
