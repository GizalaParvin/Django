from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    GET /api/health/
    Health check endpoint verifying application uptime and database connectivity.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        db_status = "connected"
        is_healthy = True

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
        except Exception as exc:
            db_status = f"unavailable: {str(exc)}"
            is_healthy = False

        payload = {
            "status": "healthy" if is_healthy else "degraded",
            "database": db_status,
            "version": "1.0.0",
            "api_endpoints": {
                "auth_register": "/api/auth/register/",
                "auth_login": "/api/auth/login/",
                "auth_refresh": "/api/auth/token/refresh/",
                "patients": "/api/patients/",
                "doctors": "/api/doctors/",
                "mappings": "/api/mappings/",
                "admin": "/admin/"
            }
        }

        http_status = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(payload, status=http_status)
