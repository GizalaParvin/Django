from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'phone', 'user', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'phone', 'user__email')
    ordering = ('-created_at',)
