import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method='filter_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_in_shopping_cart'
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        print('filter_in_shopping_cart called', value, self.request.user)

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(user_shopping_cart__user=user)
        return queryset
