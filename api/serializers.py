from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from .models import Match, User
from .utils import apply_watermark


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        """Проверяет валидность email-адреса."""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Введен некорректный адрес электронной почты!")
        return value

    def validate_gender(self, value):
        """Проверяет валидность значения пола."""
        if value not in dict(User.CHOICE_GENDER).keys():
            raise serializers.ValidationError("Введено некорректное значение пола пользователя!")
        return value

    def validate(self, attrs):
        """Проверяет, что значения полей 'password' и 'password2' совпадают."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают!"})
        return attrs

    def create(self, validated_data):
        """Создает нового пользователя, применяет водяной знак к изображению аватара и сохраняет пользователя."""
        avatar = validated_data.get('avatar')
        if avatar:
            try:
                avatar = validated_data.pop('avatar')
                validated_data['avatar'] = apply_watermark(avatar)
            except Exception as e:
                raise serializers.ValidationError("Ошибка обработки изображения: %s" % e)
        else:
            # Если аватар отсутствует, присваиваем дефолтный аватар
            validated_data['avatar'] = 'default/default_avatar.png'

        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            gender=validated_data['gender'],
            avatar=validated_data['avatar']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User - вывод списка пользователей."""

    distance = serializers.SerializerMethodField()

    def get_distance(self, obj):
        """Метод возвращает расстояние до объекта, если таковое существует"""
        if hasattr(obj, 'distance'):
            return obj.distance.km

    def to_representation(self, instance):
        """Метод проверяет есть ли радиус в запросе, если есть возвращает расстояние до пользователей,
        у которых он есть, если нет, то удаляем поле distance из response"""
        request = self.context.get('request')
        radius = request.GET.get('radius') if request else None

        # вызываем оригинальный to_representation
        ret = super().to_representation(instance)

        # удаляем поле 'distance', если радиус не указан
        if not radius and 'distance' in ret:
            ret.pop('distance')

        return ret

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'avatar', 'location', 'distance')


class MatchSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Match."""

    from_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        """Проверяет, что пользователь не лайкает себя или повторно других пользователей."""
        if attrs['from_user'] == attrs['to_user']:
            raise serializers.ValidationError({"detail": "Вы не можете лайкнуть сами себя!"})

        if Match.objects.filter(from_user=attrs['from_user'], to_user=attrs['to_user']).exists():
            raise serializers.ValidationError({"detail": "Вам уже нравился данный пользователь!"})

        return attrs

    class Meta:
        model = Match
        fields = ['from_user', 'to_user']
