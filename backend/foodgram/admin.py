from django.contrib import admin

# Register your models here.
from .models import Recipe, Tag, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('author', 'name',)
    # Добавляем интерфейс для поиска
    search_fields = ('author', 'name', 'tags')
    # Добавляем возможность фильтрации
    list_filter = ('author', 'name', 'tags',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
