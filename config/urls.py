from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from accounts.views import CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('accounts.urls')),
    path('api/users/me/', CurrentUserView.as_view(), name='users-me'),
    path('api/home/', include('home.urls')),
    path('api/', include('home.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/', include('enrollments.urls')),
    path('api/', include('legal.urls')),
    path('api/notifications/', include('home.notification_urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/contact/', include('contact.urls')),
]


