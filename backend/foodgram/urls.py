from django.urls import path

from api.views import recipe_list, tag_list, tag_detail, recipe_detail, ingredient_list, ingredient_detail
from . import views


urlpatterns = [
    # Главная страница
    path('', views.index),

    path('recipe/<int:pk>', views.recipe),
    path('user/<int:pk>', views.user),
    path('subscriptions/', views.subscriptions),
    path('favorites/', views.favorites),
    path('cart/', views.cart),
    path('pecipe/<int:pk>/pecipe_edit/', views.pecipe_edit),

    # Отдельная страница с информацией о рецепте
    # path('recipe/<pk>/', views.recipe_detail),
    path('api/tags/', tag_list, name='tag_list'),  # потом в api перенести
    path('api/recipes/', recipe_list, name='recipe_list'),  # потом в api перенести
    path('api/tags/<int:pk>/', tag_detail, name='tag_detail'),
    path('api/recipes/<int:pk>/', recipe_detail, name='recipe_detail'),
       
    path('api/ingredients/', ingredient_list, name='ingredients_list'),
    path('api/ingredients/<int:pk>/', ingredient_detail, name='ingredients_detail'),
]
