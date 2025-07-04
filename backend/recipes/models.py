from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

MIN_COOKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000
INGREDIENT_NAME_MAX_LENGTH = 128


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название",
        unique=True
    )

    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор рецепта"
    )

    name = models.CharField(
        max_length=256,
        verbose_name="Название"
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="Картинка"
    )

    text = models.TextField(
        verbose_name="Текстовое описание"
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (минуты)",
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ]
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name="Ингредиенты"
    )

    publication_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-publication_date",)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт"
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент"
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        unique_together = ('recipe', 'ingredient')
        ordering = ('recipe', 'ingredient')

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount}"
            f"{self.ingredient.measurement_unit}"
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart_items',
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name="Выбранный рецепт",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping_cart',
            ),
        ]

    def __str__(self):
        return (
            f"Пользователь {self.user} добавил рецепт "
            f"'{self.recipe.title}' в корзину"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name="Избранный рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorites',
            ),
        ]

    def __str__(self):
        return (
            f"Пользователь {self.user} добавил рецепт "
            f"'{self.recipe.title}' в избранное"
        )
