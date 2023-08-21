from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Tag(models.Model):
    class TagChoice(models.TextChoices):
        BREAKFAST = "breakfast", _("Завтрак")
        LUNCH = "lunch", _("Обед")
        DINNER = "dinner", _("Ужин")

    name = models.CharField(max_length=15, choices=TagChoice.choices)
    color = models.CharField(
        max_length=7, unique=True, verbose_name="Цветовой HEX-код"
    )
    slug = models.SlugField(
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(models.Model):
    name = models.CharField("Название ингредиента", max_length=100)
    measurement_unit = models.CharField("Единица измерения", max_length=100)

    def __str__(self):
        return self.name + " " + self.measurement_unit

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField("Название рецепта", max_length=200)
    text = models.TextField("Описание рецепта")
    cooking_time = models.PositiveIntegerField("Время приготовления")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, blank=False, related_name="recipes")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)
    image = models.ImageField("Картинка", upload_to="recipes/", blank=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipes_ingredient"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipes_ingredient"
    )
    amount = models.PositiveIntegerField("Количество")

    class Meta:
        unique_together = ["recipe", "ingredient"]
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"


class Favorite(models.Model):
    """Избранное"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_subscriber"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorite_recipe"
    )

    class Meta:
        unique_together = ["user", "recipe"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class Wishlist(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_subscriber"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="wishlist_recipe"
    )

    class Meta:
        unique_together = ["user", "recipe"]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
