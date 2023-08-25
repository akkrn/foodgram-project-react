from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, Tag, Wishlist,
)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, data: User) -> bool:
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=data.id
        ).exists()


class RecipeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowUserSerializer(UserSerializer):
    recipes_count = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj: User) -> dict:
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeAnswerSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes_count


class FollowSerializer(serializers.ModelSerializer):
    def validate(self, data: dict) -> dict:
        if data.get("author") == self.context.get("request").user:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя!"
            )
        return data

    class Meta:
        fields = ("id", "user", "author")
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны на этого автора",
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )

    def get_name(self, obj: Tag) -> str:
        return obj.get_name_display()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )

    def validate_amount(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше 0!"
            )
        return value

    def create(self, validated_data: dict) -> RecipeIngredient:
        ingredient_id = validated_data.pop("ingredient").get("id")
        ingredient = Ingredient.objects.get(id=ingredient_id)
        recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=ingredient, **validated_data
        )
        return recipe_ingredient


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source="recipes_ingredient"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "cooking_time",
            "ingredients",
            "tags",
            "image",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and Wishlist.objects.filter(user=request.user, recipe=obj).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientPostSerializer(many=True)
    author = UserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "cooking_time",
            "ingredients",
            "tags",
            "image",
        )

    def validate(self, data: dict) -> dict or ValidationError:
        if self.instance:
            return data
        name = data.get("name")
        existing_recipe = Recipe.objects.filter(name=name).first()
        if existing_recipe:
            existing_ingredients = set(
                existing_recipe.ingredients.values_list("id", flat=True)
            )
            current_ingredients_ids = []
            for ingredient_data in data.get("ingredients"):
                ingredient_id = ingredient_data.get("id")
                if ingredient_id:
                    current_ingredients_ids.append(ingredient_id)
            current_ingredients = set(current_ingredients_ids)
            if existing_ingredients == current_ingredients:
                raise serializers.ValidationError(
                    "Блюдо с таким названием и ингредиентами уже существует"
                )
        return data

    def to_representation(self, instance: Recipe) -> dict:
        serializer = RecipeGetSerializer(instance, context=self.context)
        return serializer.data

    def validate_ingredient(self, data: dict) -> dict or ValidationError:
        ingredients = data.get("ingredients")
        unique_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            if ingredient_id not in unique_ingredients:
                unique_ingredients.append(ingredient_id)
            else:
                raise ValidationError("Ингредиент уже добавлен.")
        return data

    def validate_time(self, data: dict) -> dict or ValidationError:
        if int(data.get("cooking_time")) <= 1:
            raise ValidationError("Время приготовления должно быть больше 0.")
        return data

    def create_ingredient(self, recipe: Recipe, ingredients: list) -> None:
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )

    def create(self, validated_data: dict) -> Recipe:
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        cooking_time = validated_data.pop("cooking_time")
        author = self.context.get("request").user
        new_recipe = Recipe.objects.create(
            author=author, cooking_time=cooking_time, **validated_data
        )
        new_recipe.tags.set(tags)
        self.create_ingredient(new_recipe, ingredients)
        return new_recipe

    def update(self, recipe: Recipe, validated_data: dict) -> Recipe:
        if validated_data.get("ingredients"):
            ingredients = validated_data.pop("ingredients")
            recipe.recipes_ingredient.all().delete()
            self.create_ingredient(recipe, ingredients)
        tags = validated_data.pop("tags")
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)
