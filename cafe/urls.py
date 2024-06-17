from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', main, name='main'),
    # manager_pages
    path('manager/', manager, name='manager'),
    path('manager/menu_manage/', menu_manage, name='menu_manage'),
    path('manager/menu_list/', menu_list, name='menu_list'),
    path('manager_login/', manager_login, name='manager_login'),
    path('manager/manager_logout/', manager_logout, name='manager_logout'),
    path('manager/add_item/', add_item, name='add_item'),
    path('manager/edit_item/<int:item_id>', edit_item, name='edit_item'),
    path('manager/sales/', sales, name='sales'),  # 매출 확인 페이지 URL 패턴 추가
    path('manager/manage_seats/', manage_seats, name='manage_seats'),
    path('manager/add_seat/', add_seat, name='add_seat'),
    path('manager/edit_seat/<int:seat_id>/', edit_seat, name='edit_seat'),
    path('manager/delete_seat/<int:seat_id>/', delete_seat, name='delete_seat'),
    path('toggle_seat/', toggle_seat, name='toggle_seat'),

    
    # user_pages
    path('ko_menu/', ko_menu, name='ko_menu'),
    path('en_menu/', en_menu, name='en_menu'),
    path('ja_menu/', ja_menu, name='ja_menu'),
    path('zh_menu/', zh_menu, name='zh_menu'),
    path('ko_order_type/', ko_order_type, name='ko_order_type'),
    path('en_order_type/', en_order_type, name='en_order_type'),
    path('ja_order_type/', ja_order_type, name='ja_order_type'),
    path('zh_order_type/', zh_order_type, name='zh_order_type'),
    path('ko_checkout/', ko_checkout, name='ko_checkout'),
    path('ja_checkout/', ja_checkout, name='ja_checkout'),
    path('en_checkout/', en_checkout, name='en_checkout'),
    path('zh_checkout/', zh_checkout, name='zh_checkout'),
    path('order_list/', order_list, name='order_list'),
    path('cancel_order/', cancel_order, name='cancel_order'),
    path('complete_order/', complete_order, name='complete_order'),
    path('payment/', payment, name='payment'),
    path('payment/complete/', payment_complete, name='payment_complete'),
    path('seat/', seat, name='seat'),
    path('book/<str:seat_id>/', book_seat, name='book_seat'),
    path('add_stamp/', add_stamp, name='add_stamp'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)