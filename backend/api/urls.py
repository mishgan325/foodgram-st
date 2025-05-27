from django.shortcuts import redirect, get_object_or_404
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet, IngredientViewSet, RecipeViewSet
from recipes.models import Recipe

app_name = 'api'


def short_link_redirect(request, code):
    recipe = get_object_or_404(Recipe, id=code)
    return redirect(f'../../../recipes/{recipe.id}/')


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('s/<int:code>/', short_link_redirect, name='short_link_redirect'),
    path('auth/', include('djoser.urls.authtoken')),
]
