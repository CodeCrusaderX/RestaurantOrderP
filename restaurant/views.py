from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from .models import Category, MenuItem, Table, Order, OrderItem

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            # Redirect based on group
            if user.groups.filter(name='Manager').exists():
                return redirect('manager_dashboard')
            elif user.groups.filter(name='Kitchen').exists():
                return redirect('kitchen_dashboard')
            else: # Waiter
                return redirect('index')
        else:
            return render(request, 'restaurant/login.html', {'error': 'Invalid Credentials'})
    return render(request, 'restaurant/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    if request.method == "POST":
        table_number = request.POST.get('table_number')
        table = get_object_or_404(Table, number=table_number)
        
        # Check if already occupied (Race condition prevention)
        if table.is_occupied:
            tables = Table.objects.all()
            return render(request, 'restaurant/index.html', {
                'tables': tables, 
                'error': f"Table {table.number} was just taken!"
            })
            
        # Create active order immediately to lock the table
        Order.objects.get_or_create(table=table, is_active=True)
        return redirect('menu', table_id=table.id)
    
    tables = Table.objects.all()
    return render(request, 'restaurant/index.html', {'tables': tables})

def menu(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    categories = Category.objects.prefetch_related('items').all()
    
    # Get active order if exists
    order = Order.objects.filter(table=table, is_active=True).first()
    
    # helper to get current cart quantities (items not yet "AskToPrepare" fully committed? 
    # Actually, the requirement says "Waiter checks items... AskToPrepare".
    # So we can store "cart" in session OR temporary OrderItems with status "cart" (not in model yet).
    # Since we want to ensure table items don't mix, saving to DB as 'queued' is risky if they haven't confirmed.
    # BUT, the prompt says "waiter clicks 'AskToPrepare' as soon as clicked all items... displayed to kitchen".
    # So before clicking, it's local state. 
    # However, to handle "status check" and "another customer", we need OrderItems.
    
    # Approach:
    # 1. We'll use a local JS cart for the *current selection*.
    # 2. When clicking "AskToPrepare", we POST to `submit_order`.
    # 3. `submit_order` creates OrderItems with status 'queued'.
    # 4. If an order already exists, we see previously ordered items.
    
    context = {
        'table': table,
        'categories': categories,
        'active_order': order,
    }
    return render(request, 'restaurant/menu.html', context)

def add_to_order(request):
    # This might not be needed if we submit all at once via JS.
    # But if we want to add quantity +/-, it's easier to do it client-side then bulk submit.
    return JsonResponse({'status': 'ok'})

def submit_order(request, table_id):
    if request.method == "POST":
        data = json.loads(request.body)
        items = data.get('items', []) # List of {id: item_id, quantity: qty}
        
        table = get_object_or_404(Table, id=table_id)
        order, created = Order.objects.get_or_create(table=table, is_active=True)
        
        for i in items:
            item = get_object_or_404(MenuItem, id=i['id'])
            qty = int(i['quantity'])
            if qty > 0:
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=qty,
                    status='queued'
                )
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def order_status(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    order = Order.objects.filter(table=table, is_active=True).first()
    if not order:
        return redirect('menu', table_id=table.id) # Or show empty
    
    # Group items? Or just list them.
    items = order.items.all().order_by('-created_at')
    
    return render(request, 'restaurant/status.html', {'table': table, 'order': order, 'items': items})

def bill(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    order = Order.objects.filter(table=table, is_active=True).first()
    
    if request.method == "POST":
        phone = request.POST.get('phone')
        if order:
            order.customer_phone = phone
            order.save()
            # Send (Mock) SMS
            print(f"------------ SMS SENT TO {phone} ------------")
            print(f"Bill Amount: {order.total_amount}")
            print("---------------------------------------------")
            return JsonResponse({'status': 'sent'})
            
    return render(request, 'restaurant/bill.html', {'table': table, 'order': order})

def clear_session(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    order = Order.objects.filter(table=table, is_active=True).first()
    if order:
        order.is_active = False
        order.is_paid = True # Assuming they paid if clearing
        order.save()
    return redirect('index')

# Kitchen Views
@login_required
def kitchen_dashboard(request):
    if not request.user.groups.filter(name='Kitchen').exists():
        return redirect('index')
    
    # Get all active orders items that are NOT delivered
    # Actually, kitchen wants to see "Orders" and their items.
    
    # We want to show items grouped by Table then Order.
    active_orders = Order.objects.filter(is_active=True).prefetch_related('items')
    
    # Filter only if connection has items not delivered?
    # Keeping it simple: show all active orders.
    
    return render(request, 'restaurant/kitchen.html', {'orders': active_orders})

@login_required
def update_order_status(request):
    if not request.user.groups.filter(name='Kitchen').exists():
         return JsonResponse({'status': 'Forbidden'}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_status = data.get('status')
        
        order_item = get_object_or_404(OrderItem, id=item_id)
        order_item.status = new_status
        order_item.save()
        
        return JsonResponse({'status': 'updated'})
    return JsonResponse({'status': 'error'}, status=400)

from django.db import models # Ensure models is available for F expressions locally if needed, though imported at top.

@login_required
def manager_dashboard(request):
    if not request.user.groups.filter(name='Manager').exists():
        return redirect('index')

    # Analytics
    total_revenue = 0
    paid_orders = Order.objects.filter(is_paid=True)
    for o in paid_orders:
        total_revenue += o.total_amount

    # Popular Items
    popular_items = MenuItem.objects.annotate(
        total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__is_paid=True))
    ).order_by('-total_sold')[:5]

    recent_orders = Order.objects.order_by('-created_at')[:10]

    return render(request, 'restaurant/manager_dashboard.html', {
        'revenue': total_revenue,
        'popular_items': popular_items,
        'recent_orders': recent_orders
    })

@login_required
def menu_manage(request):
    if not request.user.groups.filter(name='Manager').exists():
        return redirect('index')
    items = MenuItem.objects.all().order_by('category')
    return render(request, 'restaurant/menu_manage.html', {'items': items})

@login_required
def menu_add(request):
    if not request.user.groups.filter(name='Manager').exists(): return redirect('index')
    
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')
        cat_id = request.POST.get('category')
        
        MenuItem.objects.create(
            name=name,
            price=price,
            category_id=cat_id
        )
        return redirect('menu_manage')
        
    categories = Category.objects.all()
    return render(request, 'restaurant/menu_form.html', {'categories': categories})

@login_required
def menu_edit(request, item_id):
    if not request.user.groups.filter(name='Manager').exists(): return redirect('index')
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == "POST":
        item.name = request.POST.get('name')
        item.price = request.POST.get('price')
        item.category_id = request.POST.get('category')
        item.save()
        return redirect('menu_manage')
        
    categories = Category.objects.all()
    return render(request, 'restaurant/menu_form.html', {'categories': categories, 'item': item})

@login_required
def menu_delete(request, item_id):
    if not request.user.groups.filter(name='Manager').exists(): return redirect('index')
    item = get_object_or_404(MenuItem, id=item_id)
    if request.method == "POST":
        item.delete()
        return redirect('menu_manage')
    
    return render(request, 'restaurant/menu_delete_confirm.html', {'item': item})
