from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="istartswith"
    )

    class Meta:
        model = Recipe
        fields = ("name",)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )
    author = filters.CharFilter(lookup_expr="exact")
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="is_in_shopping_cart", method="filter"
    )
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited", method="filter"
    )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
            "is_in_shopping_cart",
            "is_favorited",
        )

    def filter(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if name == "is_in_shopping_cart" and value:
            queryset = queryset.filter(wishlist_recipe__user=self.request.user)
        if name == "is_favorited" and value:
            queryset = queryset.filter(favorite_recipe__user=self.request.user)
        return queryset
