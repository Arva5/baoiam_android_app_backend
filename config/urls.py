from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/home/', include('home.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/', include('enrollments.urls')),
    path('api/', include('my_google_auth_code.users.urls')),
    path('api/', include('legal.urls')),
    path('api/', include('courses.urls')),
]


