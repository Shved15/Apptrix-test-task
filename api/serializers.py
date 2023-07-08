from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User
from .utils import apply_watermark


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate_gender(self, value):
        if value not in dict(User.CHOICE_GENDER).keys():
            raise serializers.ValidationError("Invalid gender value")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        try:
            avatar = validated_data.pop('avatar')
            validated_data['avatar'] = apply_watermark(avatar)
        except Exception as e:
            raise serializers.ValidationError("Error processing image: %s" % e)

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
