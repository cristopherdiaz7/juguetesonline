"""
URL configuration for juguetesonline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from useradmin.simplejwt_custom import SafeTokenRefreshView
from useradmin.simplejwt_custom import ExtendedTokenObtainPairView
from useradmin.simplejwt_custom import DirectTokenObtainView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .health import health
from django.conf import settings
import os
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ventas.urls')),          # URLs para la app ventas
    path('api/user/', include('useradmin.urls')),  # URLs para la app useradmin
    # JWT endpoints
    path('api/token/', ExtendedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Alternate direct endpoint that accepts email or username and returns tokens
    path('api/token/custom/', DirectTokenObtainView.as_view(), name='token_obtain_pair_custom'),
    path('api/token/refresh/', SafeTokenRefreshView.as_view(), name='token_refresh'),
    # Lightweight ping endpoint to verify the Django app is reachable in production.
    path('api/ping/', lambda request: HttpResponse('pong'), name='api-ping'),
]


urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/health/', health),
]

# Serve media files during development or when explicitly enabled via env var.
# In production it's recommended to use a proper media/static host (S3, CDN, or webserver).
if settings.DEBUG or os.getenv('SERVE_MEDIA', '').lower() in ('1', 'true', 'yes'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



