from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time", "favorites_count")
    search_fields = ("name", "author__username", "author__first_name", "author__last_name")
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
