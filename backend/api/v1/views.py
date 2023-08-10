from django_filters.rest_framework import (
    CharFilter, DjangoFilterBackend, FilterSet,
)
from djoser.views import UserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from api.v1.permissions import IsAdmin
from api.v1.serializers import (
    FollowSerializer, IngredientSerializer, TagSerializer, UserSerializer,
)
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow, User


class IngredientViewSet(viewsets.ModelViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    pass


class UserViewSet(UserViewSet):
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def user_subscriptions(self, request):
        current_user = request.user
        subscription_list = Follow.objects.filter(subscriber=current_user)
        paginated_subscriptions = self.paginate_queryset(subscription_list)
        serialized_data = FollowSerializer(
            paginated_subscriptions, many=True, context={"request": request}
        )
        return self.get_paginated_response(serialized_data.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)
    serializer_class = FollowSerializer

    def get_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
