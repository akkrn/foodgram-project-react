from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, Tag, Wishlist,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "slug"]
    search_fields = ["name", "slug"]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "author", "cooking_time", "count_favorites"]
    search_fields = ["name", "author__username"]
    list_filter = ["author", "tags", "ingredients"]
    inlines = [
        RecipeIngredientInline,
    ]

    def count_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    count_favorites.short_description = "Сохранено"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measure_unit"]
    search_fields = ["name"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe"]
    search_fields = ["user__username", "recipe__name"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe"]
    search_fields = ["user__username", "recipe__name"]
