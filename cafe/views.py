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

import os, json 

def index(request):
    # 메인 페이지 출력
    return render(request, 'index.html')


# Manager_Pages #################################################################################################################

def manager_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'manager_id' not in request.session:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('manager_login')  # 로그인 페이지로 리디렉션
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@manager_login_required
def manager(request):
    # 메인 페이지 출력
    return render(request, 'manager_pages/manager.html')

@manager_login_required
def menu_manage(request):
    # 메인 페이지 출력
    return render(request, 'manager_pages/menu_manage.html')

def manager_login(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        password = request.POST.get('password')
        
        try:
            manager = Manager.objects.get(admin_id=admin_id)
            if manager.password == password:
                request.session['manager_id'] = manager.id
                messages.success(request, 'Successfully logged in')
                return redirect('manager')  # Replace 'dashboard' with your dashboard view name
            else:
                messages.error(request, 'Invalid password')
        except Manager.DoesNotExist:
            messages.error(request, 'Admin ID does not exist')
    
    return render(request, 'manager_pages/manager_login.html')

def manager_logout(request):
    if 'manager_id' in request.session:
        del request.session['manager_id']
        messages.success(request, 'Successfully logged out')
    return redirect('index')

def dashboard(request):
    if 'manager_id' not in request.session:
        return redirect('manager_login')
    
    # Fetch sales, menu, orders etc.
    context = {
        # 'sales': sales_data,
        # 'menu': menu_data,
        # 'orders': orders_data,
    }
    return render(request, 'dashboard.html', context)

@manager_login_required
def add_item(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            # "저장" 버튼이 클릭되었을 때 처리할 로직
            item_name = request.POST['item_name']
            item_price = request.POST['item_price']
            item_image = request.FILES.get('item_image') if 'item_image' in request.FILES else None
            category = request.POST['category']

            # 데이터 유효성 검사 및 저장
            if item_name and item_price and item_image:
                item = Item (
                    item_name = item_name,
                    item_price = item_price,
                    item_image = item_image,
                    category = category,
                )
                item.save()
                return redirect('menu_list')
            else:
                # 필요한 모든 데이터가 제출되지 않은 경우에 대한 처리
                error_message = "모든 필드를 입력해야 합니다."
        
    else:
        error_message = ""
    return render(request, 'manager_pages/add_item.html', {'error_message': error_message})

@manager_login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            # "저장" 버튼이 클릭되었을 때 처리할 로직
            item_name = request.POST['item_name']
            item_price = request.POST['item_price']
            item_image = request.FILES.get('item_image') if 'item_image' in request.FILES else item.item_image
            category = request.POST['category']

            # 데이터 유효성 검사 및 저장
            if item_name and item_price and category:
                item.item_name = item_name
                item.item_price = item_price
                item.item_image = item_image
                item.category = category
                item.save()
                return redirect('menu_list')
            else:
                # 필요한 모든 데이터가 제출되지 않은 경우에 대한 처리
                error_message = "모든 필드를 입력해야 합니다."
                return render(request, 'manager_pages/edit_item.html', {'item': item, 'error_message': error_message})
        
        elif action == 'delete':
            # "삭제" 버튼이 클릭되었을 때 처리할 로직
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
        
        # 저장 눌렀을 때
        if action == 'save':
            updated_data = {'item_name': request.POST.get('item_name'),
                            'item_price': request.POST.get('item_price'),}
            
            ori_name = request.POST.get('ori_name')
            new_name = request.POST.get('event_name')
            
            # 스탬프 모델에 데이터 저장/이미지 입력
            images = request.FILES.get('item_image')
            try:
                if images:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT))
                    filename = fs.save(images.name, images)
                    updated_data['image'] = filename
                    
                # DB에 직접 업뎃
                Item.objects.filter(event_name=ori_name).update(**updated_data)
                
                new_item_instance = Item.objects.get(item_name=new_name)  # 새로운 event_name에 해당하는 stamp 인스턴스

                # 2. 연결된 stamp_collection 레코드 찾기 및 외래 키 값 업데이트
                # related_stamp_collections = stamp_collection.objects.filter(stamp__event_name=ori_name)
                # related_stamp_collections.update(stamp=new_stamp_instance)
                
                return redirect('menu_list')  # 수정 후 도장 목록으로 리디렉션

            except Item.DoesNotExist:
                    return render(request, 'manager_pages/menu_list.html', {'error_message': '필드를 확인해주세요.'})

        # 삭제 눌렀을 때
        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')  # 삭제할 스탬프의 ID를 받아옴
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)  # 해당 ID의 스탬프 객체를 가져옴
                delstamp.delete()  # 스탬프 삭제
                
                return redirect('menu_list')  # 삭제 후 리다이렉트
            except Item.DoesNotExist:
                return render(request, 'manager_pages/menu_list.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'manager_pages/menu_list.html', {'items': items})

@manager_login_required
def order_list(request):
    orders = Order.objects.filter(is_completed=False)  # 미완료 주문만 조회
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



def get_year_range(start_year=2020):
    current_year = timezone.now().year
    return range(start_year, current_year + 1)

# User_Pages #################################################################################################################
# 쿠키 4.3 7.6 코드
# npm개념
# 시뮬라이즈
# cpu 계산

def menu(request):
    items = Item.objects.all()
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

                return redirect('menu')

            except Item.DoesNotExist:
                return render(request, 'user_pages/menu.html', {'error_message': '필드를 확인해주세요.'})

        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)
                delstamp.delete()
                
                return redirect('menu')
            except Item.DoesNotExist:
                return render(request, 'user_pages/menu.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'user_pages/menu.html', {'items': items, 'order_type': order_type})

def checkout(request):
    if request.method == 'POST':
        cart_items = request.POST.getlist('cart_items')
        total_price = request.POST.get('total_price')
        order_type = request.POST.get('order_type', 'eat_in')
        payment_type = request.POST.get('payment_type')

        if cart_items:
            new_order = Order(total_price=total_price, is_completed=False, order_type=order_type, payment_type=payment_type)
            new_order.save()

            for item_data in cart_items:
                item_details = json.loads(item_data)
                item = Item.objects.get(item_name=item_details['name'])
                OrderItem.objects.create(
                    order=new_order,
                    item=item,
                    cup_type=item_details['container'],
                    temperature=item_details['temperature'],
                    size=item_details['size'],
                    quantity=item_details['quantity'],
                    price=item_details['price']
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '주문이 성공적으로 완료되었습니다.'})

            messages.success(request, '주문이 성공적으로 완료되었습니다.')
            return redirect('menu')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': '장바구니가 비어 있습니다.'}, status=400)

            messages.error(request, '장바구니가 비어 있습니다.')

    return redirect('menu')



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
    return redirect('menu')

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
                    cup_type=item_details['container'],
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