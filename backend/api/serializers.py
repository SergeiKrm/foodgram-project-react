from django.contrib.auth.models import User
from rest_framework import serializers

from foodgram.models import Ingredient, Recipe, Tag, TagRecipe

import webcolors


class Name2HexColor(serializers.Field):
    def to_representation(self, value):
        try:
            value = webcolors.name_to_hex(value)
        except ValueError:
            raise serializers.ValidationError(
                f'Введите вместо {value} название цвета из палитры Basic Colors')
        return value
    
    def to_internal_value(self, data):
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError(
                f'Введите вместо {data} название цвета из палитры Basic Colors')
        return data



class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    # color = Name2HexColor()
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True, )
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'text', 'cooking_time')   # 'ingredients',

    '''
    def create(self, validated_data):
        # Уберем список tags из словаря validated_data и сохраним его
        tags = validated_data.pop('tags')

        # Создадим новый рецепт пока без тегов, данных нам достаточно
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_tag, status = Tag.objects.get(**tag)   # **tag
            # Поместим ссылку на каждый тег во вспомогательную таблицу, указав к какому рецепту он относится
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
        return recipe
        '''

class RecipePostSerializer(serializers.ModelField):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'name', 'text', 'cooking_time')
    
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            current_tag = Tag.objects.get(**tag)
            TagRecipe.objects.create(tag=current_tag, recipe=recipe)
        return recipe
