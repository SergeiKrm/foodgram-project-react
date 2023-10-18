from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import (
    BooleanFilter,
    FilterSet,
    ModelMultipleChoiceFilter
    )

from foodgram.models import Recipe, Tag


class CustomRecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        field_name='favorited__user',
        method='favorited_or_in_cart'
        )
    is_in_shopping_cart = BooleanFilter(
        field_name='in_cart__user',
        method='favorited_or_in_cart'
        )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def favorited_or_in_cart(self, queryset, name, value):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return queryset
        if value:
            return queryset.filter(**{name: user})
        return queryset.exclude(**{name: user})

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)
