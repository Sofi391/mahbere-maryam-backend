from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from mahberapp.views_auth import CustomTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT auth
    path('api/auth/login/',   CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),          name='token_refresh'),
    # App API
    path('api/', include('mahberapp.urls')),
    # API Docs (admin only — enforced via SPECTACULAR_SETTINGS)
    path('api/schema/',   SpectacularAPIView.as_view(),                          name='schema'),
    path('api/docs/',     SpectacularSwaggerView.as_view(url_name='schema'),     name='swagger-ui'),
    path('api/redoc/',    SpectacularRedocView.as_view(url_name='schema'),       name='redoc'),
]
