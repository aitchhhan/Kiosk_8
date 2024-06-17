from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class Member(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    stamps = models.IntegerField(default=0)
    last_stamp_date = models.DateField(null=True, blank=True)

    def add_stamp(self, count=1):
        self.stamps += count
        self.last_stamp_date = timezone.now().date()
        self.save()

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

class Seat(models.Model):
    seat_id = models.CharField(max_length=10, unique=True)
    is_available = models.BooleanField(default=True)
    row = models.IntegerField(default=0)
    column = models.IntegerField(default=0)
    
    def __str__(self):
        return self.seat_id

class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('eat_in', '먹고 가요'),
        ('take_out', '포장이요'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('cash', '현금'),
        ('card', '카드'),
        ('naver_pay', '네이버 페이'),
        ('apple_pay', '애플페이'),
    ]
    order_number = models.AutoField(primary_key=True)
    total_price = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='eat_in')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='cash')  # 새로운 필드 추가
    created_at = models.DateTimeField(default=timezone.now)  # 주문 생성 시간 필드 추가
    seat = models.ForeignKey(Seat, null=True, blank=True, on_delete=models.SET_NULL)  # 좌석 필드 추가

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