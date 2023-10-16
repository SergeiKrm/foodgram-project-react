from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views


urlpatterns = [
    # Главная страница
    # path('', views.index),

    path('recipe/<int:pk>', views.recipe),
    path('user/<int:pk>', views.user),
    path('subscriptions/', views.subscriptions),
    path('favorites/', views.favorites),
    path('cart/', views.cart),
    path('pecipe/<int:pk>/pecipe_edit/', views.pecipe_edit),


    path('api/', include('api.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)