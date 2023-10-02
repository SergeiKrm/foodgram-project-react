from django.contrib import admin

from .models import Recipe, Tag, Ingredient, TagRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('author', 'name', )
    # Добавляем интерфейс для поиска
    search_fields = ('author', 'name', 'tags')
    # Добавляем возможность фильтрации
    list_filter = ('author', 'name', 'tags',)
    inlines = (TagRecipeInline,)  # для отображения тегов М2М


class TagRecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInline,)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount',)
    list_filter = ('name',)




admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
