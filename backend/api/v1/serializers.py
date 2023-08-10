import datetime as dt

from django.core.files.base import ContentFile
from django.utils.baseconv import base64
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.shortcuts import get_object_or_404

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite,
    Wishlist,
)
from users.models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    serializer = UserSerializer(request.user, context={'request': request})

    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    username = serializers.RegexField(
        regex="^[\\w.@+-]+",
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=("username", "email"),
                message="Такой пользователь уже существует",
            ),
        ]

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=data.id
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    def validate(self, data):
        if data["following"] == self.context["request"].user:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя!"
            )
        return data

    class Meta:
        fields = ("id", "user", "following")
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="Вы уже подписаны на этого автора",
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measure_unit",
        )

    class TagSerializer(serializers.ModelSerializer):
        class Meta:
            model = Tag
            fields = (
                "name",
                "color",
                "slug",
            )


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id", required=False)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")

    def create(self, validated_data):
        ingredient_id = validated_data.pop("ingredient")["id"]
        ingredient = Ingredient.objects.get(id=ingredient_id)
        recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=ingredient, **validated_data
        )
        return recipe_ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(
        many=True, read_only=True, source="recipeingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Wishlist.objects.filter(user=request.user, recipe=obj).exists()
        )
