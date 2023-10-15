from django.contrib.auth.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from foodgram.models import Cart, Favorites, Follow, Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe


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
                'Введите название цвета из палитры "Basic Colors" '
                'https://www.w3.org/wiki/CSS/Properties/color/keywords'
                ' или укажите цветовой код в hex-формате (например, #49B64E)'
                )
        return data


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomerUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user.id
        return Follow.objects.filter(user=user, author=obj.id).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(min_value=1)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    color = Name2HexColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True,)
    author = CustomerUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True, source='ingredient_recipes')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'text', 'cooking_time',
            )

    def get_is_favorited(self, obj):
        return Favorites.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return Cart.objects.filter(recipe=obj).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = CustomerUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True, source='ingredient_recipes')
    # pub_date = serializers.HiddenField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time',
            )

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        tags = recipe['tags']
        recipe['tags'] = []
        for tag in tags:
            tag = Tag.objects.get(id=tag)
            recipe['tags'].append({
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug})
        return recipe

    @staticmethod
    def insert_ingredients(ingredient_list, recipe):
        for ingredient in ingredient_list:
            ingredient_id = ingredient['ingredient']['id']
            amount = ingredient['amount']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            IngredientRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
                )
            
    @staticmethod
    def insert_tags(tag_list, recipe):
        for tag in tag_list:
            tag = Tag.objects.get(id=tag.id)
            TagRecipe.objects.create(tag=tag, recipe=recipe)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipes')
        recipe = Recipe.objects.create(**validated_data)
        self.insert_tags(tags, recipe)
        self.insert_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        print('!!!!validated_data', validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        self.insert_ingredients(validated_data.pop('ingredient_recipes'), instance)
        self.insert_tags(validated_data.pop('tags'), instance)
        return super().update(instance, validated_data)


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(max_length=150, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
            )


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time')   # 'image' потом картинку вставить!


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time') # "image"

'''
class MeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        return False
   ''' 
class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    #recipes = RecipeFollowSerializer(many=True, read_only=True, source='author.recipes')
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user.id, author=obj.author.id).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()

    def get_recipes(self, obj):
        recipes_limit = int(
            self.context.get('request').GET.get('recipes_limit'))
        print('!!Rec!!', Recipe.objects.filter(author=obj.author))
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:recipes_limit]
        serializer = RecipeFollowSerializer(recipes, many=True, read_only=True)
        return serializer.data