from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag, TagRecipe)

User = get_user_model()


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'pub_date', 'favorited_count')
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags',)
    inlines = (TagRecipeInline, IngredientRecipeInline)

    def favorited_count(self, obj):
        return obj.favorited.count()


class TagRecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInline,)


class IngredientRecipeAdmin(admin.ModelAdmin):
    inlines = (TagRecipeInline, IngredientRecipeInline)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    list_filter = ('email', 'username')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Favorite, FavoritesAdmin)
admin.site.register(Cart, CartAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
