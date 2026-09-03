from django.urls import path
from .views import (
    CertificateDetailView,
    CertificateListView,
    UserCertificateListView,
    VerifyCertificateView,
)

urlpatterns = [
    path('', CertificateListView.as_view(), name='certificate-list'),
    path('<int:id>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('my-certificates/', UserCertificateListView.as_view(), name='user-certificates'),
    path('verify/<str:certificate_code>/', VerifyCertificateView.as_view(), name='verify-certificate'),
]

