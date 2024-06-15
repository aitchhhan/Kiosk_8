from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# class Member(models.Model):
#     phone_number = models.IntegerField(unique=True)
#     points = models.IntegerField(default=0)

#     def point_earned(self, order_price):
#         earned_points = order_price // 100
#         self.points += earned_points
#         self.save()

class Manager(models.Model):
    admin_id = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

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
    CATEGORY = [
        ('coffee', 'Coffee'),
        ('tea_ade', 'Tea / Ade'),
        ('decaffein', 'Decaffein'),
        ('dessert', 'Dessert'),
    ]
    item_name = models.CharField(max_length=255)
    item_price = models.IntegerField()
    item_image = models.ImageField(upload_to='images/')
    category = models.CharField(max_length=10, choices=CATEGORY, default='coffee')

class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('eat_in', '먹고 가요'),
        ('take_out', '포장이요'),
    ]
    order_number = models.AutoField(primary_key=True)  # 자동 증가 필드로 설정
    total_price = models.IntegerField()
    is_completed = models.BooleanField(default=False)  # 주문 완료 여부
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='eat_in')
    is_completed = models.BooleanField(default=False)  # 추가된 필드


    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.all().order_by('order_number').last()
            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1
        super().save(*args, **kwargs)

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