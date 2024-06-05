from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', main, name='main'),
    path('add_item/', add_item, name='add_item'),
    path('', coffee, name='coffee'),
    path('decaffein/', decaffein, name='decaffein'),
    path('dessert/', dessert, name='dessert'),
    path('tea_aid/', tea_aid, name='tea_aid'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)