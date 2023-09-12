from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index),

    path('recipe/<int:pk>', views.recipe),
    path('user/<int:pk>', views.user),
    path('subscribtions/', views.subscribtions),
    path('favorites/', views.favorites),
    path('cart/', views.cart),
    path('pecipe/<int:pk>/pecipe_edit/', views.pecipe_edit),
    # path('ice_cream/', views.ice_cream_list),
    # Отдельная страница с информацией о сорте мороженого
    # path('ice_cream/<pk>/', views.ice_cream_detail),
]
