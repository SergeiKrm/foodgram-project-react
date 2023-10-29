from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.fields import Base64ImageField, Name2HexColor
from api.utils import (
    get_is_in_shopping_cart,
    get_is_favorited,
    get_is_subscribed
)
from foodgram.models import (
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    TagRecipe,
)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomerUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        return get_is_subscribed(self, obj)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(min_value=1)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_id(self, value):
        try:
            get_object_or_404(Ingredient, id=value)
        except Exception:
            raise serializers.ValidationError(
                'Похоже, такого ингредиента не существует!'
            )
        return value


class TagSerializer(serializers.ModelSerializer):
    color = Name2HexColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True,)
    author = CustomerUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
        source='ingredient_recipes'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        return get_is_favorited(self, obj)

    def get_is_in_shopping_cart(self, obj):
        return get_is_in_shopping_cart(self, obj)


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    author = CustomerUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(
        many=True,
        source='ingredient_recipes',
        allow_null=False
    )
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        ingredients = data.get('ingredient_recipes')
        if ingredients == []:
            raise serializers.ValidationError(
                'Поле Ингредиенты не должно быть пустым!'
            )
        if ingredients:
            ingredients_list = []
            for element in ingredients:
                ingredients_list.append(element['ingredient'].get('id'))
            if len(ingredients) != len(set(ingredients_list)):
                raise serializers.ValidationError('Ингредиенты не уникальны!')
            return data
        return data

    def validate_tags(self, value):
        if value == []:
            raise serializers.ValidationError(
                'Поле Теги не должно быть пустым!'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги повторяются!')
        return value

    def get_is_favorited(self, obj):
        return get_is_favorited(self, obj)

    def get_is_in_shopping_cart(self, obj):
        return get_is_in_shopping_cart(self, obj)

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeSerializer(instance, context={'request': request})
        return serializer.data

    @staticmethod
    def insert_ingredients(ingredient_list, recipe):
        objects = []
        for ingredient in ingredient_list:
            ingredient_id = ingredient['ingredient']['id']
            amount = ingredient['amount']
            item = IngredientRecipe(
                ingredient_id=ingredient_id,
                recipe=recipe,
                amount=amount)
            objects.append(item)
        IngredientRecipe.objects.bulk_create(objects)

    @staticmethod
    def insert_tags(tag_list, recipe):
        objects = []
        for tag in tag_list:
            objects.append(TagRecipe(tag_id=tag.id, recipe=recipe))
        TagRecipe.objects.bulk_create(objects)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipes')
        recipe = Recipe.objects.create(**validated_data)
        self.insert_tags(tags, recipe)
        self.insert_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('ingredient_recipes'):
            instance.ingredients.clear()
            self.insert_ingredients(
                validated_data.pop('ingredient_recipes'),
                instance
            )
        else:
            raise serializers.ValidationError('Ингредиенты не указаны!')
        if validated_data.get('tags'):
            instance.tags.clear()
            self.insert_tags(validated_data.pop('tags'), instance)
        else:
            raise serializers.ValidationError('Теги не указаны!')
        return super().update(instance, validated_data)


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return get_is_subscribed(self, obj)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data
