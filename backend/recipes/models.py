from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name="Название"
    )

    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор публикации"
    )

    title = models.CharField(
        max_length=256,
        verbose_name="Название"
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="Картинка"

    )
    description = models.TextField(
        verbose_name="Текстовое описание"
    )

    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (минуты)",
        validators=[MinValueValidator(1)]
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name="Ингредиенты"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )

    amount = models.FloatField(
        verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount} {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TEXT_LENGTH_MIN, unique=True
    )
    slug = models.SlugField(
        'Слаг', max_length=TEXT_LENGTH_MIN, unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name