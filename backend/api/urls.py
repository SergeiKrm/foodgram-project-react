from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    path('', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),

]