from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from foodgram.models import Follow, Ingredient, Recipe, Tag
from .serializers import FollowSerializer, IngredientSerializer, RecipeSerializer, TagSerializer, RecipePostSerializer


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        # Если запрошенное действие (action) — получение списка объектов ('list')
        if self.action in ('list', 'retrieve',):
            # ...то применяем 
            return RecipeSerializer
        # А если запрошенное действие — не 'list', применяем 
        return RecipePostSerializer 

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class APIFollow(APIView):
    def get(self, request):
        user = self.request.user.id
        subscriptions = Follow.objects.filter(user=user)
        serializer = FollowSerializer(subscriptions, many=True)
        return Response(serializer.data)
'''
    def post(self, request):
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''
class APIPostDetail(APIView):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


'''
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer'''

    #def get_queryset(self):
    #    user = get_object_or_404(User, username=self.request.user.username)
    #    return user.follower

    #def perform_create(self, serializer):
    #    serializer.save(user=self.request.user)



'''
@api_view(['POST', 'DELETE'])   #@login_required
def follow_author(request, pk):
    # информация о текущем пользователе доступна в переменной request.user
    if request.method == 'POST':
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Сработал метод Delete', 'data': request.data})


    author = User.objects.get(pk=pk)
     




    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_200_OK)
'''


'''
@login_required
def profile_follow(request, username):
    # Подписаться на автора
    ...

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
'''