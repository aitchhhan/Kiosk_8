from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    # manager_pages
    path('manager/', manager, name='manager'),
    path('menu_manage/', menu_manage, name='menu_manage'),
    path('manager_login/', manager_login, name='manager_login'),
    path('manager_logout/', manager_logout, name='manager_logout'),
    path('add_item/', add_item, name='add_item'),
    
    
    # user_pages
    path('coffee/', coffee, name='coffee'),
    path('decaffein/', decaffein, name='decaffein'),
    path('dessert/', dessert, name='dessert'),
    path('tea_ade/', tea_ade, name='tea_ade'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)