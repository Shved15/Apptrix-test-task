from django.contrib.gis.measure import D
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Match, User
from .serializers import MatchSerializer, UserListSerializer, UserSerializer
from .tasks import send_match_email


class UserViewSet(ModelViewSet):
    """ViewSet для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListViewSet(ReadOnlyModelViewSet):
    """ViewSet для списка пользователей."""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'first_name', 'last_name']  # поля для фильтрации
    permission_classes = [IsAuthenticated]  # только для авторизованных пользователей

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('radius', openapi.IN_QUERY, type=openapi.TYPE_NUMBER)
    ])
    def list(self, request, *args, **kwargs):
        """Возвращает список пользователей с возможностью фильтрации по радиусу."""
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Возвращает queryset пользователей с примененным фильтром по радиусу, если пользователь аутентифицирован."""
        queryset = super().get_queryset()
        user = self.request.user
        radius = self.request.query_params.get('radius', None)  # Получение значения query-параметра 'radius'

        # Проверка аутентификации пользователя и наличия значения 'radius'
        if user.is_authenticated and radius:
            point = user.location
            # Фильтрация queryset по радиусу
            queryset = queryset.filter(location__distance_lte=(point, D(km=float(radius))))

        return queryset


class MatchViewSet(ModelViewSet):
    """ViewSet для модели Match."""

    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def create(self, request, *args, **kwargs):
        """Создает новый матч и отправляет уведомления об образовавшейся паре."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Проверка наличия обратного матча (пары) в базе данных
        if Match.objects.filter(from_user=serializer.validated_data['to_user'],
                                to_user=serializer.validated_data['from_user']).exists():

            # Получаем пользователей кто создал матч и к которому создан матч
            to_user = serializer.validated_data['to_user']
            from_user = serializer.validated_data['from_user']

            # Отправка уведомлений замэтчиным пользователям по электронной почте
            send_match_email.delay(
                to_email=to_user.email,
                match_name=from_user.first_name  # Получаем имя участника
            )
            send_match_email.delay(
                to_email=from_user.email,
                match_name=to_user.first_name
            )
            return Response(
                {"match": f"У вас есть пара! Почта участника: {to_user.email}"},
                status=status.HTTP_201_CREATED
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
