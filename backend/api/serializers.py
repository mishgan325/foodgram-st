import base64
import uuid
from foodgram_backend.settings import AUTH_USER_MODEL
from django.core.files.base import ContentFile
from rest_framework import serializers

# from foodgram_backend.constants import IMAGE
# from recipes.models import (
#     Favorite,
#     Ingredient,
#     Recipe,
#     RecipeIngredient,
#     ShoppingCart,
#     Tag,
# )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserGetSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(allow_null=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = AUTH_USER_MODEL
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        """Проверка подписки пользователей."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.subscribers.filter(author=author).exists()
        )
