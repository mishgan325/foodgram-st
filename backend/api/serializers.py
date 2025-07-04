from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from rest_framework import serializers

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient)
from users.models import Subscription

from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000


class UserPostSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class FoodgramUserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = fields

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=author).exists()


class UserGetSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
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
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=author).exists()


class AvatarUpdateSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    def update(self, instance, validated_data):
        avatar_data = validated_data.get('avatar')
        instance.avatar = avatar_data
        instance.save()
        return instance


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id', 'name', 'measurement_unit', 'amount'
        ]


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT,
                                      max_value=MAX_INGREDIENT_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserGetSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shopping_cart_items.filter(recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        required=True
    )

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'image', 'name', 'text', 'cooking_time'
        ]

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Необходимо изображение.')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент.'
            )
        ingredient_ids = [
            item['id'].id if isinstance(item['id'], Ingredient)
            else item['id'] for item in value
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        return value

    def create_ingredients(self, ingredients_data, recipe):
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })

        instance.recipe_ingredients.all().delete()
        self.create_ingredients(ingredients_data, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('subscriber', 'author')
        read_only_fields = ('subscriber',)

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if user.subscriptions.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def create(self, validated_data):
        validated_data['subscriber'] = self.context['request'].user
        return super().create(validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = serializers.ImageField(source='author.avatar', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        if limit:
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
