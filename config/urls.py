"""
URL configuration for healthcare_backend project.
"""

from django.contrib import admin
from django.urls import path, include
from .views import HealthCheckView

urlpatterns = [
    path('', HealthCheckView.as_view(), name='root-overview'),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/mappings/', include('mappings.urls')),
]
