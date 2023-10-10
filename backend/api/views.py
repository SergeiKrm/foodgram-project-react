import io
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet
from reportlab.pdfgen import canvas
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram.models import Cart, Favorites, Follow, Ingredient, Recipe, Tag, IngredientRecipe
from .serializers import ShortRecipeSerializer, FollowSerializer, IngredientSerializer, RecipeSerializer, TagSerializer, RecipePostSerializer


User = get_user_model()


def to_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return RecipeSerializer
        return RecipePostSerializer 

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = Favorites.objects.filter(
            user=self.request.user,
            recipe=recipe
            )

        if self.request.method == 'POST':
            if favorite_recipe.exists():
                return Response(
                    {'Error massage': 'Рецепт уже есть в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            Favorites.objects.create(user=self.request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if favorite_recipe.exists():
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Error massage': 'Рецепт не был добавлен  в избранное!'},
            status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_in_cart = Cart.objects.filter(
            user=self.request.user,
            recipe=recipe
            )

        if self.request.method == 'POST':
            if recipe_in_cart.exists():
                return Response(
                    {'Error massage': 'Рецепт уже есть в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            Cart.objects.create(user=self.request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if recipe_in_cart.exists():
            recipe_in_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Error massage': 'Рецепт отсутствует в списке покупок!'},
            status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(recipe__in_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(total_amount = Sum('amount'))
        print('!!amount!', ingredients)
        
        # Работает ли отправка pdf пока не знаю!!!
        text = 'тут текст'
        pdf = to_pdf(text)
      
        #return Response({'massage':'ничего'}, status=status.HTTP_204_NO_CONTENT)
        return FileResponse(pdf)







class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class APIFollow(APIView):
    def get(self, request):
        user = self.request.user.id
        subscriptions = Follow.objects.filter(user=user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)
    

class APIFollowDetail(APIView):  # пока можно создать дубликат
    def post(self, request, id):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        new_subscription = Follow.objects.create(
            user=self.request.user,
            author=author
            )

        serializer = FollowSerializer(new_subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        subscription = get_object_or_404(
            Follow,
            user=self.request.user.id,
            author=self.kwargs.get('id')
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



