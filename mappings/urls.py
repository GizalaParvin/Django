from django.urls import path
from .views import MappingListCreateView, MappingDetailOrPatientView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('<int:pk>/', MappingDetailOrPatientView.as_view(), name='mapping-detail-or-patient'),
]
