from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.models import Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe


import webcolors


class Name2HexColor(serializers.Field):
    def to_representation(self, value):
        return value
    
    def to_internal_value(self, data):
        if data[0] == '#':
            return data
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError(
                'Введите название цвета из палитры "Basic Colors" https://www.w3.org/wiki/CSS/Properties/color/keywords'
                ' или укажите цветовой код в hex-формате (например, #49B64E)'
                )
        return data


class IngredientAmountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField() # source='ingredient.id'
    amount = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')



class CustomerUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=False)    # функционал is_subscribed не сделан еще!

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

'''
class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')   # !!!выведет id+amount или весь список
'''

class TagSerializer(serializers.ModelSerializer):
    color = Name2HexColor()
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True,)
    author = CustomerUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True, source='ingredient_recipes')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text', 'cooking_time')


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = CustomerUserSerializer(read_only=True)
    ingredients = IngredientAmountPostSerializer(many=True, source='ingredient_recipes')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipes')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            tag = Tag.objects.get(id=tag.id)
            TagRecipe.objects.create(tag=tag, recipe=recipe)

        for ingredient in ingredients:
            ingredient_id = list(ingredient.items())[0][1]
            amount = int(list(ingredient.items())[1][1])
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
                )
        return recipe


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(max_length=150, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password',)
