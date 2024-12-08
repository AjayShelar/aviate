from django.urls import path
from .views import CandidateCreateView, CandidateUpdateDeleteView, CandidateSearchView

urlpatterns = [
    path('candidates/', CandidateCreateView.as_view(), name='candidate-list-create'),
    path('candidates/<int:pk>/', CandidateUpdateDeleteView.as_view(), name='candidate-update-delete'),
    path('candidates/search/', CandidateSearchView.as_view(), name='candidate-search'),
]