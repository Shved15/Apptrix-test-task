from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db import models as gismodels
from django.db import models


class UserManager(BaseUserManager):
    """Создает и сохраняет нового пользователя с обязательными данными: email, имя, фамилия и пол."""

    def create_user(self, email, first_name, last_name, gender, password=None):
        if not email:
            raise ValueError('У пользователя должен быть email!')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Модель пользователя"""

    CHOICE_GENDER = (
        ('M', 'Men'),
        ('W', 'Women'),
    )

    email = models.EmailField(verbose_name='email address', max_length=255, unique=True,)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=CHOICE_GENDER)
    avatar = models.ImageField(upload_to='avatars/', default='default/default_avatar.png')
    location = gismodels.PointField(null=True, blank=True, geography=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # Поле для входа в систему
    USERNAME_FIELD = 'email'
    # Обязательные поля при создании пользователя
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender', 'avatar']

    def __str__(self):
        """Возвращает строковое представление пользователя (его email)."""
        return self.email


class Match(models.Model):
    """Модель, хранящая matches."""
    from_user = models.ForeignKey(User, related_name='matches_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='matches_to', on_delete=models.CASCADE)
    matched = models.BooleanField(default=False)
