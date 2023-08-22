from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    Wishlist,
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

    def count_favorites(self, obj: Recipe) -> int:
        return Favorite.objects.filter(recipe=obj).count()

    count_favorites.short_description = "Сохранено"

    def get_queryset(self, request: admin.ModelAdmin) -> Recipe:
        qs = super().get_queryset(request)
        return qs.selected_related("author").prefetch_related(
            "tags", "ingredients"
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    search_fields = ("recipe__name", "ingredient__name")

    def get_queryset(self, request: admin.ModelAdmin) -> RecipeIngredient:
        qs = super().get_queryset(request)
        return qs.select_related("recipe", "ingredient")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "measurement_unit"]
    search_fields = ["name"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe"]
    search_fields = ["user__username", "recipe__name"]

    def get_queryset(self, request: admin.ModelAdmin) -> Favorite:
        qs = super().get_queryset(request)
        return qs.select_related("user", "recipe")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe"]
    search_fields = ["user__username", "recipe__name"]

    def get_queryset(self, request: admin.ModelAdmin) -> Wishlist:
        qs = super().get_queryset(request)
        return qs.select_related("user", "recipe")
