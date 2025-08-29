from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Client  
from django.db import transaction
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Cart, CartItem, Order, Client, OrderItem
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.core.paginator import Paginator

from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date, parse_time
from datetime import datetime, timedelta, time
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncMonth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.template.response import TemplateResponse




import logging
import json, logging


def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'signup.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # ✅ Just create empty Client profile (used for linking orders, tracking points, etc.)
        Client.objects.create(user=user)

        login(request, user)
        messages.success(request, f'Welcome, {first_name}! Your account has been created.')
        return redirect('home')

    return render(request, 'signup.html')


def signin_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # ✅ redirect to homepage
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'signin.html')

def password_view(request):
    return render(request, 'forgot-password.html')  

def controler_view(request):
    return render(request, 'controler.html')  

def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('home')


def home_view(request):
    products = Product.objects.filter(available=True)[:8]  # only available products
    return render(request, 'home.html', {'products': products})


def store_list(request):
    return render(request, 'store-list.html')



def shop_grid(request): 
    subcategory = request.GET.get('subcategory')
    type_choices = Product.TYPE_CHOICES

    all_products = Product.objects.all()

    if subcategory:
        products_to_display = all_products.filter(subcategory=subcategory)
    else:
        products_to_display = all_products

    # Build sidebar filters from all products
    categories = all_products.values_list('category', flat=True).distinct()
    subcategories_by_category = []
    for cat in categories:
        subcats = all_products.filter(category=cat).values_list('subcategory', flat=True).distinct()
        subcategories_by_category.append((cat, list(subcats)))

    # Apply pagination
    paginator = Paginator(products_to_display, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Determine dynamic title
    title = "All Categories"
    if subcategory:
        for cat, subcats in subcategories_by_category:
            if subcategory in subcats:
                title = f"{cat} - {subcategory}"
                break

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'subcategories_by_category': subcategories_by_category,
        'type_choices': type_choices,
        'selected_title': title,
    }
    return render(request, 'shop-grid.html', context)






def settings_view(request):
    return render(request, 'settings.html') 

def address_view(request):
    return render(request, 'address.html')   

def notification_view(request):
    return render(request, 'notification.html')

def checkout_view(request):
    return render(request, 'shop-checkout.html')  

def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@require_POST
def add_to_cart(request):
    try:
        print("🔹 Received request:", request.body)
        data = json.loads(request.body)
        product_id = data.get("product_id")
        size = data.get("size")
        quantity = int(data.get("quantity", 1))
    except Exception as e:
        print("❌ JSON parse error:", e)
        return JsonResponse({"error": "Invalid input"}, status=400)

    if not product_id or not size:
        print("❌ Missing product_id or size")
        return JsonResponse({"error": "Missing data"}, status=400)

    try:
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if not cart:
                cart = Cart.objects.create(user=request.user, is_active=True)
        else:
            if not request.session.session_key:
                request.session.create()
                request.session.save()

            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key, is_active=True).first()
            if not cart:
                cart = Cart.objects.create(session_key=session_key, is_active=True)

        # ✅ Move this outside the `if-else` block
        cart_item = CartItem.objects.filter(cart=cart, product=product, size=size).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            CartItem.objects.create(cart=cart, product=product, size=size, quantity=quantity)

        
        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Unexpected error:", e) 
        print("📦 CART:", cart)
        print("📦 CART ITEMS:", cart.items.all() if cart else "No cart")
        return JsonResponse({"error": "Something went wrong"}, status=500)



def cart_sidebar_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key, is_active=True).first()

    print("🛒 CART:", cart)
    if cart:
        print("🛒 CART ITEMS COUNT:", cart.items.count())
        for item in cart.items.all():
            print("📦", item, "| Qty:", item.quantity)
    else:
        print("⚠️ No cart found.")

    return render(request, "partials/cart_offcanvas_body.html", {"cart": cart})


def get_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key, is_active=True).first()

    if not cart:
        cart = Cart.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=None if request.user.is_authenticated else session_key,
            is_active=True
        )
    return cart



def checkout_view(request):
    cart = get_cart(request)
    cart_items = cart.items.select_related('product')
    
    item_subtotal = sum(item.product.price * item.quantity for item in cart_items)
    service_fee = Decimal("3.00")  # ✅ Use Decimal, not float
    total = item_subtotal + service_fee


    context = {
        "cart": cart,
        "cart_items": cart_items,
        "item_subtotal": item_subtotal,
        "service_fee": service_fee,
        "total": total,
    }
    return render(request, "shop-checkout.html", context)


@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        print("⚠️ RAW BODY:", request.body)

        try:
            data = json.loads(request.body)
        except Exception as e:
            print("❌ JSON LOAD ERROR:", str(e))
            return JsonResponse({'error': 'Invalid JSON body', 'details': str(e)}, status=400)

        phone = data.get('phone')
        address = data.get('address')
        day = data.get('delivery_day')
        time_str = data.get('delivery_time')

        today = datetime.today().date()
        if day == "today":
            delivery_day = today
        elif day == "tomorrow":
            delivery_day = today + timedelta(days=1)
        else:
            weekday_map = {
                "monday": 0, "tuesday": 1, "wednesday": 2,
                "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
            }
            delivery_day = today + timedelta((weekday_map[day.lower()] - today.weekday()) % 7)

        # Convert hour like "10-11am" to 10:00
        try:
            delivery_time = datetime.strptime(time_str.split('-')[0].strip(), "%I").time()
        except:
            delivery_time = time(10, 0)  # fallback

        cart = get_cart(request)

        sum_price = sum(item.product.price * item.quantity for item in cart.items.all())
        delivery_price = 0
        total_price = sum_price + delivery_price

        # 🔐 Save to session for confirm_order to use later
        request.session['pending_order_summary'] = {
            'phone': phone,
            'address': address,
            'delivery_day': str(delivery_day),  # str for JSON serializability
            'delivery_time': delivery_time.strftime('%H:%M:%S'),
        }

        html = render_to_string('partials/order_summary_modal_body.html', {
            'cart': cart,
            'phone': phone,
            'address': address,
            'delivery_day': delivery_day,
            'delivery_time': delivery_time,
            'sum_price': sum_price,
            'delivery_price': delivery_price,
            'total_price': total_price
        })

        return JsonResponse({'html': html})
    
logger = logging.getLogger(__name__)

@require_POST
def confirm_order(request):
    logger.info("🔄 confirm_order view was called")

    summary = request.session.get('pending_order_summary')
    if not summary:
        logger.warning("❌ Missing summary in session")
        return JsonResponse({'success': False, 'error': 'Missing summary'}, status=400)

    # Get all active carts for current user or session
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, is_active=True)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        carts = Cart.objects.filter(session_key=session_key, is_active=True)

    if not carts.exists():
        logger.warning("❌ No active cart found")
        return JsonResponse({'success': False, 'error': 'No active cart'}, status=400)

    # Use the first cart to attach to order
    cart = carts.first()

    if hasattr(cart, 'order'):
        logger.info("⚠️ This cart has already been ordered")
        request.session.pop('pending_order_summary', None)
        return JsonResponse({'success': True, 'alreadyOrdered': True})

    logger.info("✅ Proceeding to create order")

    client = getattr(request.user, 'client', None) if request.user.is_authenticated else None

    order = Order.objects.create(
        client=client,
        phone=summary['phone'],
        address=summary['address'],
        delivery_day=summary['delivery_day'],
        delivery_time=summary['delivery_time'],
        cart=cart,
        sum_price=sum(item.product.price * item.quantity for item in cart.items.all()),
        delivery_price=0,
        total_price=sum(item.product.price * item.quantity for item in cart.items.all()),
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            size=item.size,
            quantity=item.quantity,
            price_at_order=item.product.price
        )

    # ✅ Deactivate ALL carts related to this user/session
    for c in carts:
        c.is_active = False
        c.save()

    request.session.pop('pending_order_summary', None)
    request.session.pop('cart_id', None)  # if you use this anywhere

    logger.info(f"✅ Order {order.id} created successfully")

    messages.success(request, "✅ Your order was placed successfully!")
    return JsonResponse({'success': True, 'redirect_url': '/'})


@login_required
def user_orders_view(request):
    user = request.user
    client = Client.objects.filter(user=user).first()

    if not client:
        orders = []
    else:
        orders = Order.objects.filter(client=client).prefetch_related('items__product').order_by('-created_at')

    return render(request, 'orders.html', {
        'orders': orders,
        'client': client,
    })


@staff_member_required
def custom_admin_index(request):
    # Earnings (monthly revenue)
    monthly_revenue = Order.objects.filter(
        created_at__month=now().month,
        created_at__year=now().year
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Orders count
    total_orders = Order.objects.count()
    new_orders = Order.objects.filter(created_at__gte=now()-timedelta(days=2)).count()

    # Customers count
    total_customers = User.objects.count()
    new_customers = User.objects.filter(date_joined__gte=now()-timedelta(days=2)).count()

    recent_orders = Order.objects.order_by('-created_at')[:5]

    shippings_total = Order.objects.aggregate(total=Sum('shipping_price'))['total'] or 0
    refunds_total = Order.objects.aggregate(total=Sum('refund_amount'))['total'] or 0
    orders_total = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    income_total = orders_total - refunds_total  # Example logic

    chart_data = {
        'labels': ['Shippings', 'Refunds', 'Orders', 'Income'],
        'values': [shippings_total, refunds_total, orders_total, income_total]
    }

    context = {
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'new_orders': new_orders,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'recent_orders': recent_orders,
        'chart_data': chart_data,
        **admin.site.each_context(request),

          
    }
    return TemplateResponse(request, 'admin/index.html', context)


