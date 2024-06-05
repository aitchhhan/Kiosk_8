from django.shortcuts import render, redirect
from .models import *
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

def index(request):
    # 메인 페이지 출력
    return render(request, 'index.html')

# def main(request):
#     # 메인 페이지 출력
#     return render(request, 'main.html')
  
def coffee(request):
    # 메인 페이지 출력
    return render(request, 'coffee.html')

def decaffein(request):
    # 메인 페이지 출력
    return render(request, 'decaffein.html')

def dessert(request):
    # 메인 페이지 출력
    return render(request, 'dessert.html')

def tea_aid(request):
    # 메인 페이지 출력
    return render(request, 'tea_aid.html')

# def menu(request):
#     # 메뉴 목록 출력
#     items = Item.objects.all()
#     return render(request, 'menu.html', {'items': items})

# def order(request):
#     # 주문 처리
#     if request.method == 'POST':
#         order_number = request.POST['order_number']
#         total_price = request.POST['total_price']

#         member = Member.objects.get(user=request.user)
#         order = Order.objects.create(member=member, order_number=order_number, total_price=total_price)

#         for item_id, quantity in request.POST.items():
#             if item_id.startswith('item_'):
#                 item_id = int(item_id.split('_')[1])
#                 item = Item.objects.get(id=item_id)
#                 OrderItem.objects.create(order=order, item=item, quantity=quantity)

#         return redirect('order_complete')
#     else:
#         items = Item.objects.all()
#         return render(request, 'order.html', {'items': items})

# def order_complete(request):
#     # 주문 완료 페이지 출력
#     return render(request, 'order_complete.html')



# def manager_login(request):
#     # 관리자 로그인 처리
#     if request.method == 'POST':
#         admin_id = request.POST['admin_id']
#         password = request.POST['password']

#         try:
#             manager = Manager.objects.get(admin_id=admin_id)
#         except Manager.DoesNotExist:
#             return render(request, 'manager_login.html', {'error_message': '존재하지 않는 관리자입니다.'})

#         if manager.password != password:
#             return render(request, 'manager_login.html', {'error_message': '비밀번호가 틀렸습니다.'})

#         request.session['manager_id'] = manager.id
#         return redirect('manager_main')
#     else:
#         return render(request, 'manager_login.html')

# def manager_logout(request):
#     # 관리자 로그아웃 처리
#     del request.session['manager_id']
#     return redirect('manager_login')

# def manager_main(request):
#     # 관리자 메인 페이지 출력
#     return render(request, 'manager_main.html')

# def manage_menu(request):
#     # 메뉴 관리 페이지 출력
#     if request.method == 'POST':
#         name = request.POST['name']
#         price = request.POST['price']
#         image = request.FILES['image']
#         cup_type = request.POST['cup_type']
#         temperature = request.POST['temperature']
#         size = request.POST['size']

#         Item.objects.create(name=name, price=price, image=image, cup_type=cup_type, temperature=temperature, size=size)
#         return redirect('manage_menu')


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
                return redirect('coffee')
            else:
                # 필요한 모든 데이터가 제출되지 않은 경우에 대한 처리
                error_message = "모든 필드를 입력해야 합니다."
        
    else:
        error_message = ""

    return render(request, 'add_item.html', {'error_message': error_message})

def coffee(request):
    items = Item.objects.filter(category='coffee')
    
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
                
                return redirect('coffee')  # 수정 후 도장 목록으로 리디렉션

            except Item.DoesNotExist:
                    return render(request, 'coffee.html', {'error_message': '필드를 확인해주세요.'})

        # 삭제 눌렀을 때
        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')  # 삭제할 스탬프의 ID를 받아옴
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)  # 해당 ID의 스탬프 객체를 가져옴
                delstamp.delete()  # 스탬프 삭제
                
                return redirect('coffee')  # 삭제 후 리다이렉트
            except Item.DoesNotExist:
                return render(request, 'coffee.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'coffee.html', {'items': items})

def decaffein(request):
    items = Item.objects.filter(category='decaffein')
    
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
                
                return redirect('decaffein')  # 수정 후 도장 목록으로 리디렉션

            except Item.DoesNotExist:
                    return render(request, 'decaffein.html', {'error_message': '필드를 확인해주세요.'})

        # 삭제 눌렀을 때
        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')  # 삭제할 스탬프의 ID를 받아옴
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)  # 해당 ID의 스탬프 객체를 가져옴
                delstamp.delete()  # 스탬프 삭제
                
                return redirect('decaffein')  # 삭제 후 리다이렉트
            except Item.DoesNotExist:
                return render(request, 'decaffein.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'decaffein.html', {'items': items})

def dessert(request):
    items = Item.objects.filter(category='dessert')
    
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
                
                return redirect('dessert')  # 수정 후 도장 목록으로 리디렉션

            except Item.DoesNotExist:
                    return render(request, 'dessert.html', {'error_message': '필드를 확인해주세요.'})

        # 삭제 눌렀을 때
        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')  # 삭제할 스탬프의 ID를 받아옴
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)  # 해당 ID의 스탬프 객체를 가져옴
                delstamp.delete()  # 스탬프 삭제
                
                return redirect('dessert')  # 삭제 후 리다이렉트
            except Item.DoesNotExist:
                return render(request, 'dessert.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'dessert.html', {'items': items})

def tea_aid(request):
    items = Item.objects.filter(category='tea_aid')
    
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
                
                return redirect('tea_aid')  # 수정 후 도장 목록으로 리디렉션

            except Item.DoesNotExist:
                    return render(request, 'tea_aid.html', {'error_message': '필드를 확인해주세요.'})

        # 삭제 눌렀을 때
        if action == 'delete':
            ori_stamp = request.POST.get('ori_name')  # 삭제할 스탬프의 ID를 받아옴
            
            try:
                delstamp = Item.objects.get(event_name=ori_stamp)  # 해당 ID의 스탬프 객체를 가져옴
                delstamp.delete()  # 스탬프 삭제
                
                return redirect('tea_aid')  # 삭제 후 리다이렉트
            except Item.DoesNotExist:
                return render(request, 'tea_aid.html', {'error_message': '이벤트가 존재하지 않습니다.'})
    
    return render(request, 'tea_aid.html', {'items': items})