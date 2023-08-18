import datetime

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from djoser.views import UserViewSet

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from recipes.models import Recipe, Ingredient, Tag, Favorite, Wishlist
from users.models import User, Follow

from api.v1.serializers import (
    UserSerializer,
    FollowSerializer,
    FollowUserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeFollowSerializer,
)

from api.v1.permissions import OwnerOnly, IsAdmin
from api.v1.filters import IngredientFilter, RecipeFilter


class UserViewSet(UserViewSet):
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
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
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = FollowSerializer(
                data={"author": author.id, "user": request.user.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = FollowUserSerializer(author,
                                              context={"request": request})
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
    filter_backends = (IngredientFilter,)



class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    filterset_fields = (
        "author", "tags",
        #"is_favorited", "is_in_shopping_cart")
    )
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
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
        user = request.user
        if request.method == "POST":
            model.objects.get_or_create(user=user, recipe=recipe)
            return Response({"success": True}, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[OwnerOnly],
    )
    def download_shopping_cart(self, request, pk):
        user = request.user
        ingredients = (
            Wishlist.objects.filter(user=user)
                .values(
                "recipe__ingredients__name",
                "recipe__ingredients__unit",
            )
                .annotate(total_amount=Sum("recipe__ingredients__amount"))
        )

        ingredients_list = [
            f"{ingredient['recipe__ingredients__name']} - "
            f"{ingredient['total_amount']} "
            f"{ingredient['recipe__ingredients__unit']}"
            for ingredient in ingredients
        ]

        ingredients_str = "\n".join(ingredients_list)
        response = HttpResponse(ingredients_str, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = f"attachment; filename=shopping_cart_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeFollowSerializer
    pagination_class = None
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        return self.request.user.favorite_subscriber.all()
