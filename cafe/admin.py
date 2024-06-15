from django.contrib import admin
from .models import Manager, Item, OrderItem, Order

# admin.site.register(Member)
admin.site.register(Manager)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)

# Register your models here.
