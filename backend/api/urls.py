from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, APIFollow


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
# router.register('users/(?P<post_id>\\d+)/comments', FollowViewSet, basename='comment')


urlpatterns = [
    path('', include(router.urls)),

    path('users/subscriptions/', APIFollow.as_view()),   # !! Follow

    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    path('', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    # path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),

]
