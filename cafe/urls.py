from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    # manager_pages
    path('manager/', manager, name='manager'),
    path('manager/menu_manage/', menu_manage, name='menu_manage'),
    path('manager/menu_list/', menu_list, name='menu_list'),
    path('manager/manager_login/', manager_login, name='manager_login'),
    path('manager/manager_logout/', manager_logout, name='manager_logout'),
    path('manager/add_item/', add_item, name='add_item'),
    path('manager/edit_item/<int:item_id>', edit_item, name='edit_item'),
    
    
    # user_pages
    path('menu/', menu, name='menu'),
    path('checkout/', checkout, name='checkout'),
    path('order_list/', order_list, name='order_list'),
    path('cancel_order/', cancel_order, name='cancel_order'),
    path('complete_order/', complete_order, name='complete_order'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)