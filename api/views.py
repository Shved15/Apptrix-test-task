from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import User
from .serializers import UserSerializer, UserListSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'first_name', 'last_name']
