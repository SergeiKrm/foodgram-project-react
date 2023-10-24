import base64
import webcolors

from django.core.files.base import ContentFile
from rest_framework import serializers


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
