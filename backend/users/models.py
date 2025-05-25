from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    username = models.CharField(
        "Никнейм",
        unique=True,
        max_length=150,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
            )
        ],
        error_messages={
            'unique': 'Никнейм занят.',
        },
    )

    first_name = models.CharField(
        "Имя",
        max_length=150,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        "Фамилия",
        max_length=150,
        blank=False,
        null=False
    )

    email = models.EmailField(
        "Электронная почта",
        unique=True,
        max_length=254,
        blank=False,
        null=False
    )

    avatar = models.ImageField(
        "Аватар",
        upload_to='avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscribers',
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецептов',
        related_name='authors',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('subscriber',)
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscriber_author'
            ),
            models.CheckConstraint(
                name='check_subscriber_author',
                check=~models.Q(subscriber=models.F('author')),
            )
        ]

    def __str__(self):
        return f'Подписка {self.subscriber} на {self.author}'
