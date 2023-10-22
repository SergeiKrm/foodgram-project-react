import base64
import webcolors

from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram.models import Cart, Favorite, Follow


class Name2HexColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if data[0] == '#':
            return data
        try:
            data = webcolors.name_to_hex(data)
        except ValueError:
            raise serializers.ValidationError(
                'Введите название цвета из палитры "Basic Colors" '
                'https://www.w3.org/wiki/CSS/Properties/color/keywords'
                ' или укажите цветовой код в hex-формате (например, #49B64E)'
            )
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def get_is_subscribed(self, obj):
    user = self.context.get('request').user
    if not user.is_authenticated:
        return False
    if hasattr(obj, 'author'):
        return Follow.objects.filter(user=user, author=obj.author.id).exists()
    return Follow.objects.filter(user=user, author=obj.id).exists()


def get_is_favorited(self, obj):
    user = self.context.get('request').user
    if user.is_authenticated:
        return Favorite.objects.filter(user=user, recipe=obj).exists()
    return False


def get_is_in_shopping_cart(self, obj):
    user = self.context.get('request').user
    if user.is_authenticated:
        return Cart.objects.filter(user=user, recipe=obj).exists()
    return False
