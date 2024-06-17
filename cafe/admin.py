from django.contrib import admin
from .models import Member, Manager, Item, OrderItem, Order, Seat

admin.site.register(Member)
admin.site.register(Manager)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Seat)

# Register your models here.
