from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient


RECIPE_INGREDIENT_INLINE_EXTRA = 1
RECIPE_INGREDIENT_INLINE_MIN_NUM = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = RECIPE_INGREDIENT_INLINE_EXTRA
    min_num = RECIPE_INGREDIENT_INLINE_MIN_NUM


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time", "favorites_count")
    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__last_name"
    )
    list_filter = ("author",)
    ordering = ("name",)
    inlines = [RecipeIngredientInline]

    @admin.display(description="В избранном у пользователей")
    def favorites_count(self, recipe):
        return recipe.favorite_recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", "recipe_count")
    search_fields = ("name",)
    list_filter = ("measurement_unit", )
    ordering = ("name",)

    @admin.display(description="Число рецептов")
    def recipe_count(self, ingredient):
        return ingredient.recipe_ingredients.count()
