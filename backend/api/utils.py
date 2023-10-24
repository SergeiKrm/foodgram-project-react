from foodgram.models import Cart, Favorite, Follow


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
