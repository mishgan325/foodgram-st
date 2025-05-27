import os

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import models
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient, Recipe, RecipeIngredient
from users.models import Subscription
from .filters import RecipeFilter
from .models import ShoppingCart, Favorite
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarUpdateSerializer,
    IngredientSerializer,
    SubscriptionCreateSerializer,
    SubscriptionReadSerializer,
    UserGetSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    ShortRecipeSerializer,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserGetSerializer
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def update_avatar(self, request):
        user = request.user
        if request.method == "DELETE":
            if user.avatar and user.avatar.name != "users/image.png":
                if hasattr(user.avatar, 'path'):
                    default_storage.delete(user.avatar.path)
                else:
                    user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response({"avatar": None},
                            status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)
        return Response(
            {"avatar": user.avatar.url if user.avatar else None},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        author = self.get_object()
        user = request.user
        if request.method == 'POST':
            data = {'author': author.id}
            serializer = SubscriptionCreateSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            subscription = serializer.save()
            read_serializer = SubscriptionReadSerializer(
                subscription, context={'request': request}
            )
            return Response(read_serializer.data,
                            status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(subscriber=user,
                                                   author=author)
        if not subscription.exists():
            raise ValidationError('Вы не подписаны на этого пользователя.')
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(
            subscriber=user
        ).select_related('author')
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionReadSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name_param = self.request.query_params.get('name')
        if name_param:
            queryset = queryset.filter(name__istartswith=name_param)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        'recipe_ingredients__ingredient'
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in [
            'create', 'favorite', 'shopping_cart', 'download_shopping_cart'
        ]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        elif self.action == 'get_link':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        short_link = request.build_absolute_uri(f'/api/s/{pk}')
        return Response({"short-link": short_link})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в корзине.')
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not cart_item.exists():
            raise ValidationError('Рецепта нет в корзине.')
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__user_shopping_cart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total_amount=models.Sum('amount'))
            .order_by('ingredient__name')
        )
        font_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static',
            'fonts',
            'DejaVuSans.ttf'
        )
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50
        p.setFont("DejaVuSans", 16)
        p.drawString(50, y, "Список покупок")
        y -= 30
        p.setFont("DejaVuSans", 12)
        if not ingredients:
            p.drawString(50, y, "Корзина пуста.")
        else:
            for idx, item in enumerate(ingredients, 1):
                line = (
                    f"{idx}. {item['ingredient__name']} "
                    f"— {item['total_amount']} "
                    f"{item['ingredient__measurement_unit']}"
                )
                p.drawString(50, y, line)
                y -= 20
                if y < 50:
                    p.showPage()
                    y = height - 50
                    p.setFont("Helvetica", 12)
        p.showPage()
        p.save()
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError('Рецепт уже в избранном.')
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            raise ValidationError('Рецепта нет в избранном.')
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
