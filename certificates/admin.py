from django.contrib import admin
from .models import Certificate, UserCertificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'issuer_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'issuer_name')


@admin.register(UserCertificate)
class UserCertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'certificate', 'certificate_code', 'issued_at', 'is_verified')
    list_filter = ('is_verified', 'issued_at')
    search_fields = ('user__email', 'certificate__title', 'certificate_code')

