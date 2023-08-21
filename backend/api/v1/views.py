from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend, filters
from djoser.views import UserViewSet
from filters import RecipeFilter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import Favorite, Ingredient, Recipe, Tag, Wishlist
from users.models import Follow, User

from .serializers import (
    FollowSerializer, FollowUserSerializer, IngredientSerializer,
    RecipeAnswerSerializer, RecipeGetSerializer, RecipeSerializer,
    TagSerializer,
)


class UserViewSet(UserViewSet):
    @action(
        detail=False,
        methods=["get"],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user.id
        ).order_by("id")
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
    def subscribe(self, request, id):
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
            follow = get_object_or_404(
                Follow, user=request.user, author=author
            )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    queryset = Ingredient.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeGetSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
    )
    def favorite(self, request, pk):
        return self._toggle_relation(Favorite, request, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self._toggle_relation(Wishlist, request, pk)

    def _toggle_relation(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeAnswerSerializer(
            recipe, context={"request": request}
        )
        user = request.user
        if request.method == "POST":
            model.objects.get_or_create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            Wishlist.objects.filter(user=user)
                .values(
                "recipe__recipes_ingredient__ingredient__name",
                "recipe__recipes_ingredient__ingredient__measurement_unit",
            )
                .annotate(
                total_amount=Sum("recipe__recipes_ingredient__amount"))
        )
        ingredients_str = (
            "Данный список покупок составлен в сервисе "
            "Foodgram\n\n"
            "Список покупок:"
        )
        for ingredient in ingredients:
            ingredients_list = [
                f"{ingredient['recipe__recipes_ingredient__ingredient__name']} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['recipe__recipes_ingredient__ingredient__measurement_unit']}"
            ]
            ingredients_str += "\n" + "\n".join(ingredients_list)

        response = HttpResponse(ingredients_str, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = f"attachment; filename=shopping_cart_{datetime.now().strftime('%Y%m%d')}.txt"
        return response
