from django.contrib import admin
from django.urls import path, include
from accounts.views import CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/users/me/', CurrentUserView.as_view(), name='users-me'),
    path('api/home/', include('home.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/', include('enrollments.urls')),
    path('api/', include('legal.urls')),
]


