from django.contrib import admin

from .models import Follow, Recipe, Tag, Ingredient, TagRecipe, IngredientRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('id', 'author', 'name', )
    # Добавляем интерфейс для поиска
    search_fields = ('author', 'name', 'tags')
    # Добавляем возможность фильтрации
    list_filter = ('author', 'name', 'tags',)
    inlines = (TagRecipeInline, IngredientRecipeInline)  # для отображения тегов М2М


class TagRecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInline,)


class IngredientRecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInline, IngredientRecipeInline)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    #list_filter = ('name',)



admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Follow, FollowAdmin)