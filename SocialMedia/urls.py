from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet

from .utils import schema_view

router = DefaultRouter()
router.register(r'clients/create', UserViewSet, basename='create-client')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
