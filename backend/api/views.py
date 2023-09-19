from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from foodgram.models import Ingredient, Recipe, Tag
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer

# Create your views here.
@api_view(['GET'])
def tag_list(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tag_detail(request, pk):
    tag = Tag.objects.get(pk=pk)
    serializer = TagSerializer(tag)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET', 'POST'])
def recipe_list(request):
    if request.method == 'POST':
        serializer = RecipeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    recipes = Recipe.objects.all()
    serializer = RecipeSerializer(recipes, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PATCH', 'DELETE'])
def recipe_detail(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    if request.method == 'PATCH':
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = RecipeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    serializer = IngredientSerializer(ingredients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ingredient_detail(request, pk):
    ingredient = Ingredient.objects.get(pk=pk)
    serializer = IngredientSerializer(ingredient)
    return Response(serializer.data, status=status.HTTP_200_OK)