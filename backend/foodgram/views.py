from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


# Главная страница
def index(request):
    return HttpResponse('Главная страница')


def recipe(request):  # над урл еще подумать
    return HttpResponse('Страница рецепта')  # Здесь — полное описание рецепта.


def user(request):
    return HttpResponse('Страница пользователя')


def subscribtions(request):
    return HttpResponse('Страница подписок')


def favorites(request):
    return HttpResponse('Избранное')


def cart(request):
    return HttpResponse('Cписок покупок')


def pecipe_edit(request):
    return HttpResponse('Cоздание и редактирование рецепта')
