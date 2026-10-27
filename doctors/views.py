from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for doctor directory and management.
    - Read operations (list, retrieve): Any authenticated user can view doctors.
    - Create: Any authenticated user can register a doctor (associated via created_by).
    - Update/Delete: Scoped strictly to the creator; attempts by other users return 404.
    """
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Doctor.objects.none()

        # Enforce distinct read vs write queryset:
        # Non-creators attempting to modify/delete get HTTP 404
        if self.action in ['update', 'partial_update', 'destroy']:
            return Doctor.objects.filter(created_by=self.request.user)

        queryset = Doctor.objects.all().order_by('-created_at')

        # Query parameter filtering
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization.strip())

        search = self.request.query_params.get('search')
        if search:
            query = search.strip()
            queryset = queryset.filter(
                models.Q(name__icontains=query) |
                models.Q(specialization__icontains=query) |
                models.Q(qualification__icontains=query)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Doctor created successfully.",
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
                "message": "Doctor updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Doctor deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
