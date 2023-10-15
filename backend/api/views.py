import io
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import CustomRecipeFilter
from foodgram.models import Cart, Favorites, Follow, Ingredient, Recipe, Tag, IngredientRecipe
from .pagination import PageLimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import CustomerUserSerializer, FollowSerializer, IngredientSerializer, RecipeSerializer, ShortRecipeSerializer, TagSerializer, RecipePostSerializer


User = get_user_model()


def to_pdf(to_pdf):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    textob = p.beginText()   # !!!
    textob.textLine(to_pdf)



    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, to_pdf)
    #p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="cart.pdf")


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # filterset_fields = ('author', 'tags', )  #'is_favorited'
    filterset_class = CustomRecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_permissions(self):
        if self.action == 'download_shopping_cart':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

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

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(recipe__in_cart__user=request.user.id).values(
            'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(total_amount=Sum('amount'))

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        MyFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
        pdfmetrics.registerFont(MyFontObject)
        pdf.setFont("Arial", 12)
        pdf.drawString(200, 750, "Список покупок")
        x, y = 100, 725
        for element in ingredients:
            string = (f'• {element["ingredient__name"]} '
                      f'({element["ingredient__measurement_unit"]}) — '
                      f'{element["total_amount"]}')
            pdf.drawString(x, y, string)
            y -= 25
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="cart.pdf")


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

'''
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomerUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination # PageNumberPagination

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        subscription = Follow.objects.filter(user=user, author=author)

        if self.request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'Error massage': 'Подписка уже существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Error massage': 'Такой подписки не существует!'},
            status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user.id
        subscriptions = Follow.objects.filter(user=user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=False)
    def me(self, request):
        user = User.objects.get(id=self.request.user.id)
        serializer = MeSerializer(user)
        return Response(serializer.data)'''
    


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        if self.action == 'subscriptions':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = self.request.user.id
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
            )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = self.request.user
        subscription = Follow.objects.filter(user=user, author=author)

        if self.request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'Error massage': 'Подписка уже существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            subscription = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Error massage': 'Такой подписки не существует!'},
            status=status.HTTP_400_BAD_REQUEST
            )