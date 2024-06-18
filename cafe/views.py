from django.shortcuts import get_object_or_404, render, redirect
from functools import wraps
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, datetime
from django import template

import os, json 

def main(request):
    return render(request, 'main.html')

def ko_order_type(request):
    return render(request, 'user_pages/ko/ko_order_type.html')

def en_order_type(request):
    return render(request, 'user_pages/en/en_order_type.html')

def ja_order_type(request):
    return render(request, 'user_pages/ja/ja_order_type.html')

def zh_order_type(request):
    return render(request, 'user_pages/zh/zh_order_type.html')


# Manager_Pages #################################################################################################################

def manager_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'manager_id' not in request.session:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('manager_login')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@manager_login_required
def manager(request):
    return render(request, 'manager_pages/manager.html')

@manager_login_required
def menu_manage(request):
    return render(request, 'manager_pages/menu_manage.html')

def manager_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        
        try:
            manager = Manager.objects.get(admin_id=admin_id)
            if manager.password == password:
                request.session['manager_id'] = manager.id
                messages.success(request, '로그인 성공')
                return redirect('manager')  
            else:
                messages.error(request, '유효하지 않은 비밀번호')
        except Manager.DoesNotExist:
            messages.error(request, '아이디가 존재하지 않음')
    
    return render(request, 'manager_pages/manager_login.html')

def manager_logout(request):
    if 'manager_id' in request.session:
        del request.session['manager_id']
        messages.success(request, '로그아웃 성공')
    return redirect('manager')

@manager_login_required
def add_item(request):
    error_message = ""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            item_name_ko = request.POST.get('item_name_ko')
            item_name_en = request.POST.get('item_name_en')
            item_name_ja = request.POST.get('item_name_ja')
            item_name_zh = request.POST.get('item_name_zh')
            item_price = request.POST.get('item_price')
            item_image = request.FILES.get('item_image') if 'item_image' in request.FILES else None
            category = request.POST.get('category')

            if item_name_ko and item_name_en and item_name_ja and item_name_zh and item_price and item_image and category:
                item = Item(
                    item_name_ko=item_name_ko,
                    item_name_en=item_name_en,
                    item_name_ja=item_name_ja,
                    item_name_zh=item_name_zh,
                    item_price=item_price,
                    item_image=item_image,
                    category=category,
                )
                item.save()
                return redirect('menu_list')
            else:
                error_message = "모든 필드를 입력해야 합니다."
        
    return render(request, 'manager_pages/add_item.html', {'error_message': error_message})

@manager_login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            item_name_ko = request.POST.get('item_name_ko')
            item_name_en = request.POST.get('item_name_en')
            item_name_ja = request.POST.get('item_name_ja')
            item_name_zh = request.POST.get('item_name_zh')
            item_price = request.POST.get('item_price')
            item_image = request.FILES.get('item_image') if 'item_image' in request.FILES else None
            category = request.POST.get('category')

            if item_name_ko and item_name_en and item_name_ja and item_name_zh and item_price and category:
                item.item_name_ko = item_name_ko
                item.item_name_en = item_name_en
                item.item_name_ja = item_name_ja
                item.item_name_zh = item_name_zh
                item.item_price = item_price
                if item_image:
                    item.item_image = item_image                
                item.category = category
                item.save()
                return redirect('menu_list')
            else:
                error_message = "모든 필드를 입력해야 합니다."
                return render(request, 'manager_pages/edit_item.html', {'item': item, 'error_message': error_message})
        
        elif action == 'delete':
            item.delete()
            return redirect('menu_list')
    
    else:
        error_message = ""

    return render(request, 'manager_pages/edit_item.html', {'item': item, 'error_message': error_message})


@manager_login_required
def menu_list(request):
    items = Item.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                return redirect('menu_list')  

            except Item.DoesNotExist:
                    return render(request, 'manager_pages/menu_list.html', {'error_message': '필드를 확인해주세요.'})
    
    return render(request, 'manager_pages/menu_list.html', {'items': items})

@manager_login_required
def order_list(request):
    orders = Order.objects.filter(is_completed=False)  
    return render(request, 'manager_pages/order_list.html', {'orders': orders})

@manager_login_required
def sales(request):
    now = timezone.now()
    
    selected_date = request.GET.get('date', None)
    selected_month = request.GET.get('month', None)
    selected_year = request.GET.get('year', None)

    completed_orders = Order.objects.filter(is_completed=True)

    if selected_date:
        start_of_selected_day = datetime.strptime(selected_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_selected_day = start_of_selected_day + timedelta(days=1)
        day_sales = completed_orders.filter(created_at__gte=start_of_selected_day, created_at__lt=end_of_selected_day).aggregate(Sum('total_price'))['total_price__sum'] or 0
    else:
        day_sales = None

    if selected_month:
        start_of_selected_month = datetime.strptime(selected_month, '%Y-%m').replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_selected_month = (start_of_selected_month + timedelta(days=31)).replace(day=1)
        month_sales = completed_orders.filter(created_at__gte=start_of_selected_month, created_at__lt=end_of_selected_month).aggregate(Sum('total_price'))['total_price__sum'] or 0
    else:
        month_sales = None

    if selected_year:
        start_of_selected_year = datetime.strptime(selected_year, '%Y').replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_selected_year = start_of_selected_year.replace(year=start_of_selected_year.year + 1)
        year_sales = completed_orders.filter(created_at__gte=start_of_selected_year, created_at__lt=end_of_selected_year).aggregate(Sum('total_price'))['total_price__sum'] or 0
    else:
        year_sales = None

    total_sales = completed_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0

    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + timedelta(days=1)
    today_sales = completed_orders.filter(created_at__gte=start_of_today, created_at__lt=end_of_today).aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'completed_orders': completed_orders,
        'day_sales': day_sales,
        'month_sales': month_sales,
        'year_sales': year_sales,
        'total_sales': total_sales,
        'today_sales': today_sales,
        'selected_date': selected_date,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'year_range': get_year_range(),
    }
    return render(request, 'manager_pages/sales.html', context)

register = template.Library()

@register.filter
def to_range(value, max_value):
    return range(value, max_value + 1)

@register.filter
def get_item(sequence, position):
    try:
        return sequence[position - 1]
    except IndexError:
        return None

@manager_login_required
def manage_seats(request):
    seats = Seat.objects.all()
    return render(request, 'manager_pages/manage_seats.html', {'seats': seats})

@manager_login_required
def add_seat(request):
    if request.method == 'POST':
        seat_id = request.POST['seat_id']
        row = request.POST['row']
        column = request.POST['column']
        if seat_id and row and column:
            Seat.objects.create(seat_id=seat_id, row=row, column=column)
            messages.success(request, '좌석이 성공적으로 추가되었습니다.')
            return redirect('manage_seats')
        else:
            messages.error(request, '모든 필드를 입력해야 합니다.')
    return render(request, 'manager_pages/add_seat.html')

@manager_login_required
def edit_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    if request.method == 'POST':
        seat.seat_id = request.POST['seat_id']
        seat.row = request.POST['row']
        seat.column = request.POST['column']
        seat.save()
        messages.success(request, '좌석이 성공적으로 수정되었습니다.')
        return redirect('manage_seats')
    return render(request, 'manager_pages/edit_seat.html', {'seat': seat})

@manager_login_required
def delete_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    seat.delete()
    messages.success(request, '좌석이 성공적으로 삭제되었습니다.')
    return redirect('manage_seats')

def get_year_range(start_year=2020):
    current_year = timezone.now().year
    return range(start_year, current_year + 1)

@csrf_exempt
def toggle_seat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            seat_id = data.get('seat_id')
            seat = get_object_or_404(Seat, seat_id=seat_id)
            seat.is_available = not seat.is_available
            seat.save()
            return JsonResponse({'success': True})
        except Seat.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Seat does not exist'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def cancel_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(order_number=order_id)
            order.delete()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '주문이 존재하지 않습니다.'}, status=400)
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)

@csrf_exempt
def complete_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(order_number=order_id)
            order.is_completed = True
            order.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '주문이 존재하지 않습니다.'}, status=400)
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)

# User_Pages #################################################################################################################

def ko_menu(request):
    items = Item.objects.all()
    seats = Seat.objects.all()  
    order_type = request.GET.get('order_type', 'eat_in')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                new_item_instance = Item.objects.get(item_name=new_name)

                return redirect('ko_menu')

            except Item.DoesNotExist:
                return render(request, 'user_pages/ko/ko_menu.html', {'error_message': '필드를 확인해주세요.'})
    
    return render(request, 'user_pages/ko/ko_menu.html', {'items': items, 'seats': seats, 'order_type': order_type})

def en_menu(request):
    items = Item.objects.all()
    seats = Seat.objects.all()  
    order_type = request.GET.get('order_type', 'eat_in')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                new_item_instance = Item.objects.get(item_name=new_name)

                return redirect('en_menu')

            except Item.DoesNotExist:
                return render(request, 'user_pages/en/en_menu.html', {'error_message': '필드를 확인해주세요.'})
    
    return render(request, 'user_pages/en/en_menu.html', {'items': items, 'seats': seats, 'order_type': order_type})

def ja_menu(request):
    items = Item.objects.all()
    seats = Seat.objects.all()  
    order_type = request.GET.get('order_type', 'eat_in')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                new_item_instance = Item.objects.get(item_name=new_name)

                return redirect('ja_menu')

            except Item.DoesNotExist:
                return render(request, 'user_pages/ja/ja_menu.html', {'error_message': '필드를 확인해주세요.'})
    
    return render(request, 'user_pages/ja/ja_menu.html', {'items': items, 'seats': seats, 'order_type': order_type})

def zh_menu(request):
    items = Item.objects.all()
    seats = Seat.objects.all()  
    order_type = request.GET.get('order_type', 'eat_in')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                new_item_instance = Item.objects.get(item_name=new_name)

                return redirect('zh_menu')

            except Item.DoesNotExist:
                return render(request, 'user_pages/zh/zh_menu.html', {'error_message': '필드를 확인해주세요.'})
    
    return render(request, 'user_pages/zh/zh_menu.html', {'items': items, 'seats': seats, 'order_type': order_type})

def ko_checkout(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')
        payment_type = request.POST.get('payment_type')
        seat_id = request.POST.get('seat_id')  

        if cart_items:
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type=payment_type)
            if seat_id:
                seat = Seat.objects.get(seat_id=seat_id)
                new_order.seat = seat  
                seat.is_available = False
                seat.save()
            new_order.save()

            for item_data in cart_items:
                item_details = json.loads(item_data)
                item = Item.objects.get(item_name_ko=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})

            messages.success(request, '주문이 성공적으로 완료되었습니다.')
            return redirect('main')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '장바구니가 비어 있습니다.'}, status=400)

            messages.error(request, '장바구니가 비어 있습니다.')

    return redirect('ko_menu')

def ja_checkout(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')
        payment_type = request.POST.get('payment_type')
        seat_id = request.POST.get('seat_id')  

        if cart_items:
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type=payment_type)
            if seat_id:
                seat = Seat.objects.get(seat_id=seat_id)
                new_order.seat = seat  
                seat.is_available = False
                seat.save()
            new_order.save()

            for item_data in cart_items:
                item_details = json.loads(item_data)
                item = Item.objects.get(item_name_ja=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})

            messages.success(request, '주문이 성공적으로 완료되었습니다.')
            return redirect('main')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '장바구니가 비어 있습니다.'}, status=400)

            messages.error(request, '장바구니가 비어 있습니다.')

    return redirect('ja_menu')

def en_checkout(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')
        payment_type = request.POST.get('payment_type')
        seat_id = request.POST.get('seat_id')  

        if cart_items:
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type=payment_type)
            if seat_id:
                seat = Seat.objects.get(seat_id=seat_id)
                new_order.seat = seat  
                seat.is_available = False
                seat.save()
            new_order.save()

            for item_data in cart_items:
                item_details = json.loads(item_data)
                item = Item.objects.get(item_name_en=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})

            messages.success(request, '주문이 성공적으로 완료되었습니다.')
            return redirect('main')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '장바구니가 비어 있습니다.'}, status=400)

            messages.error(request, '장바구니가 비어 있습니다.')

    return redirect('en_menu')

def zh_checkout(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')
        payment_type = request.POST.get('payment_type')
        seat_id = request.POST.get('seat_id')  

        if cart_items:
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type=payment_type)
            if seat_id:
                seat = Seat.objects.get(seat_id=seat_id)
                new_order.seat = seat  
                seat.is_available = False
                seat.save()
            new_order.save()

            for item_data in cart_items:
                item_details = json.loads(item_data)
                item = Item.objects.get(item_name_zh=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})

            messages.success(request, '주문이 성공적으로 완료되었습니다.')
            return redirect('main')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '장바구니가 비어 있습니다.'}, status=400)

            messages.error(request, '장바구니가 비어 있습니다.')

    return redirect('zh_menu')

@csrf_exempt
def payment(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')

        if cart_items:
            context = {
                'cart_items': cart_items,
                'total': total_price,
                'counter': len(cart_items),
                'order_type': order_type,
            }
            return render(request, 'user_pages/payment.html', context)
    return redirect('ko_menu')

@csrf_exempt
def payment_complete(request):
    if request.method == 'POST':
        imp_uid = request.POST.get('imp_uid')
        merchant_uid = request.POST.get('merchant_uid')
        paid_amount = request.POST.get('paid_amount')
        status = request.POST.get('status')
        cart_items = json.loads(request.POST.get('cart_items'))
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type')

        if status == 'paid':
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type='card')
            new_order.save()

            for item_data in cart_items:
                item_details = item_data
                item = Item.objects.get(item_name=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            messages.success(request, '결제가 성공적으로 완료되었습니다.')
            return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})
        else:
            return JsonResponse({'message': '결제 실패.'}, status=400)
    return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)

@csrf_exempt
def add_stamp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            member, created = Member.objects.get_or_create(phone_number=phone_number)
            today = timezone.now().date()
            if member.last_stamp_date == today:
                return JsonResponse({'message': '오늘은 이미 적립하셨습니다. 내일 다시 적립해주세요.'}, status=400)
            member.add_stamp(1)
            message = '스탬프가 적립되었습니다.'
            if created:
                message += ' 신규 회원이 등록되었습니다.'
            return JsonResponse({'message': message})
        else:
            return JsonResponse({'message': '전화번호를 입력해주세요.'}, status=400)
    return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)