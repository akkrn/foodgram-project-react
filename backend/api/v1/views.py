from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import Favorite, Ingredient, Recipe, Tag, Wishlist
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    FollowSerializer,
    FollowUserSerializer,
    IngredientSerializer,
    RecipeAnswerSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
    TagSerializer,
)
from recipes.utils import generate_shopping_cart


class UserViewSet(UserViewSet):
    @action(
        detail=False,
        methods=["get"],
    )
    def subscriptions(self, request: HttpResponse) -> HttpResponse:
        queryset = (
            User.objects.filter(following__user=request.user.id)
            .order_by("id")
            .anotate(recipes_count=Count("recipes"))
        )
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
    )
    def subscribe(self, request: HttpResponse, id: int) -> HttpResponse:
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = FollowSerializer(
                data={"author": author.id, "user": request.user.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = FollowUserSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if Follow.objects.filter(
                author=author, user=request.user
            ).delete():
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)
    queryset = Ingredient.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.select_related(
        "author"
    ).prefetch_related("tags", "ingredients")

    def get_serializer_class(self) -> RecipeSerializer:
        if self.action in ["list", "retrieve"]:
            return RecipeGetSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
    )
    def favorite(self, request: HttpResponse, id: int) -> HttpResponse:
        return self._toggle_relation(Favorite, request, id)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request: HttpResponse, id: int) -> HttpResponse:
        return self._toggle_relation(Wishlist, request, id)

    def _toggle_relation(
        self, model: Any, request: HttpResponse, id: int
    ) -> HttpResponse:
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeAnswerSerializer(
            recipe, context={"request": request}
        )
        user = request.user
        if request.method == "POST":
            model.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if model.objects.filter(user=user, recipe=recipe).delete():
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request: HttpResponse) -> HttpResponse:
        ingredients = (
            Wishlist.objects.filter(user=request.user)
            .values(
                "recipe__recipes_ingredient__ingredient__name",
                "recipe__recipes_ingredient__ingredient__measurement_unit",
            )
            .annotate(total_amount=Sum("recipe__recipes_ingredient__amount"))
        )
        buffer = generate_shopping_cart(ingredients)
        response = HttpResponse(buffer.getvalue(), content_type="text/plain")
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping_cart.txt"
        return response
