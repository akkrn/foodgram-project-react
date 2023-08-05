from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (
    UserViewSet, TagViewSet, RecipeViewSet, IngredientViewSet,
    TokenView, MeView, SetPasswordsView, FollowView, FavoriteView,
    ShoppingCartView
)

app_name = "api"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("auth/token/login", TokenView.as_view(), name="login"),
    path("auth/token/logout", TokenView.as_view(), name="logout"),
    path("users/me/", MeView.as_view(), name="user_detail"),
    path("users/set_passwords/", SetPasswordsView.as_view(), name="set_password"),
    path("users/subscriptions/", FollowView.as_view(), name="subscriptions"),
    path('recipes/<int:id>/favorite/', FavoriteView.as_view(), name='favorite'),
    path("recipes/download_shopping_cart/", ShoppingCartView.as_view(), name="shopping_cart"),
    path("", include(router.urls)),
]
