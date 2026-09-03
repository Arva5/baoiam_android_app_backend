from django.urls import path

from .views import AcceptLegalDocumentView, LegalDocumentView

urlpatterns = [
    path("legal/accept/", AcceptLegalDocumentView.as_view(), name="legal-accept"),
    path("legal/<str:doc_type>/", LegalDocumentView.as_view(), name="legal-document"),
]