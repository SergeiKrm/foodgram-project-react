import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import CustomRecipeFilter, CustomIngredientFilter
from foodgram.models import (Cart, Favorite, Follow, Ingredient,
                             IngredientRecipe, Recipe, Tag)
from .pagination import PageLimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)

User = get_user_model()


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

    def post_delete_detail_method(self, request, pk,
                                  Model,
                                  post_bad_request_text,
                                  delete_bad_request_text):
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Exception:
            return Response(
                {'Похоже, такого рецепта не существует!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        filtered_recipes = Model.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        exists = filtered_recipes.exists()
        if self.request.method == 'POST':
            if exists:
                return Response(
                    {post_bad_request_text},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Model.objects.create(user=self.request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if exists:
            filtered_recipes.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {delete_bad_request_text},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        post_bad_request_text = 'Рецепт уже есть в избранном!'
        delete_bad_request_text = 'Рецепт отсутствует в избранном!'
        return self.post_delete_detail_method(request,
                                              pk,
                                              Favorite,
                                              post_bad_request_text,
                                              delete_bad_request_text)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        post_bad_request_text = 'Рецепт уже есть в списке покупок!'
        delete_bad_request_text = 'Рецепт отсутствует в списке покупок!'
        return self.post_delete_detail_method(request,
                                              pk,
                                              Cart,
                                              post_bad_request_text,
                                              delete_bad_request_text)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__in_cart__user=request.user.id).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    total_amount=Sum('amount'))
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        MyFontObject = ttfonts.TTFont('arial', 'arial.ttf')
        pdfmetrics.registerFont(MyFontObject)
        pdf.setFont('arial', 12)
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
    filter_backends = (CustomIngredientFilter,)
    search_fields = ('^name',)


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
            if user == author:
                return Response(
                    {'Error massage': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscription.exists():
                return Response(
                    {'Error massage': 'Подписка уже существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                subscription, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Error massage': 'Такой подписки не существует!'},
            status=status.HTTP_400_BAD_REQUEST
        )
