from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.models import Ingredient, Recipe, Tag, TagRecipe


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


class CustomerUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=False)    # функционал is_subscribed не сделан еще!

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    color = Name2HexColor()
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True, )
    author = CustomerUserSerializer(read_only=True)
        
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'text', 'cooking_time')   # 'ingredients',

    
class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = CustomerUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'text', 'cooking_time')
    
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            tag = Tag.objects.get(id=tag.id)
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        return recipe


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(max_length=150, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password',)

