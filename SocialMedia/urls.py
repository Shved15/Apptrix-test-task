from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import MatchViewSet, UserListViewSet, UserViewSet

from .utils import schema_view

router = DefaultRouter()
router.register(r'clients/create', UserViewSet, basename='create-client')
router.register(r'list', UserListViewSet, basename='user-list')
router.register(r'clients/(?P<from_user_id>\d+)/match', MatchViewSet, basename='match')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
