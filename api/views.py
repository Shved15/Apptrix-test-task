from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Match, User
from .serializers import MatchSerializer, UserListSerializer, UserSerializer
from .tasks import send_match_email


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'first_name', 'last_name']


class MatchViewSet(ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if Match.objects.filter(from_user=serializer.validated_data['to_user'],
                                to_user=serializer.validated_data['from_user']).exists():
            send_match_email.delay(serializer.validated_data['from_user'].email,
                                   serializer.validated_data['to_user'].email)
            send_match_email.delay(serializer.validated_data['to_user'].email,
                                   serializer.validated_data['from_user'].email)
            return Response({"match": f"You have a match! Email: {serializer.validated_data['to_user'].email}"},
                            status=status.HTTP_201_CREATED)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
