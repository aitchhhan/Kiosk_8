from django.db import models

# class Member(models.Model):
#     phone_number = models.CharField(max_length=15)
#     points = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return self.phone_number

# class Item(models.Model):
#     name = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image = models.ImageField(upload_to='items/')

#     def __str__(self):
#         return self.name

# class OrderItem(models.Model):
#     CUP_CHOICES = [
#         ('regular', 'Regular'),
#         ('large', 'Large'),
#     ]
#     TEMP_CHOICES = [
#         ('hot', 'Hot'),
#         ('iced', 'Iced'),
#     ]
#     SIZE_CHOICES = [
#         ('small', 'Small'),
#         ('medium', 'Medium'),
#         ('large', 'Large'),
#     ]

#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     cup_type = models.CharField(max_length=10, choices=CUP_CHOICES)
#     temperature = models.CharField(max_length=4, choices=TEMP_CHOICES)
#     size = models.CharField(max_length=6, choices=SIZE_CHOICES)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def save(self, *args, **kwargs):
#         self.price = self.item.price * self.quantity
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f'{self.quantity} x {self.item.name}'

# class Order(models.Model):
#     member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     order_items = models.ManyToManyField(OrderItem)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     def save(self, *args, **kwargs):
#         self.total_price = sum(item.price for item in self.order_items.all())
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f'Order {self.id} by {self.member.phone_number}'


class Member(models.Model):
    phone_number = models.IntegerField(unique=True)
    points = models.IntegerField(default=0)

    def point_earned(self, order_price):
        earned_points = order_price // 100
        self.points += earned_points
        self.save()

class Manager(models.Model):
    admin_id = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def manage_menu(self):
        # 메뉴 관리 기능 구현
        pass

    def manage_order(self):
        # 주문 관리 기능 구현
        pass

    def check_sales(self):
        # 판매 현황 확인 기능 구현
        pass

class Item(models.Model):
    item_name = models.CharField(max_length=255)
    item_price = models.IntegerField()
    item_image = models.ImageField(upload_to='images/')
    

class Order(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    order_number = models.IntegerField(unique=True)
    total_price = models.IntegerField()

    def check_total_price(self):
        total_price = 0
        for order_item in self.orderitem_set.all():
            total_price += order_item.price * order_item.quantity
        self.total_price = total_price
        self.save()

    def cart(self):
        # 장바구니 기능 구현
        pass

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cup_type = models.CharField(max_length=255)
    temperature = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def add_to_cart(self, quantity):
        self.quantity = quantity
        self.price = self.item.price * self.quantity
        self.save()

    def view_details(self):
        # 주문 상세 보기 기능 구현
        pass
