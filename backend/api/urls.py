from django.urls import path

from .views import tag_list

urlpatterns = [
    path('api/tags/', tag_list, name='tag_list'),
]