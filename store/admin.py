from django.contrib import admin
from .models import Product, Order, Cart, CartItem,Client ,ProductStock, Order, OrderItem  # Add all your models here
from .forms import ProductForm  # import your form
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.contrib.auth.models import User

from store.models import Order

from django.contrib import admin
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from store.models import Order
import calendar
import json


from datetime import datetime, timedelta, time
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncMonth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse


admin.site.register(Client)
admin.site.register(Cart)
admin.site.register(CartItem)

class ProductAdmin(admin.ModelAdmin):
    form = ProductForm


class ProductStockInline(admin.TabularInline):  # Or use admin.StackedInline for more vertical layout
    model = ProductStock
    extra = 5  # Number of blank rows shown — enough for S, M, L, XL, XXL
    min_num = 1
    max_num = 5

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'available']
    inlines = [ProductStockInline]

@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'quantity']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'size', 'quantity', 'price_at_order']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'delivery_day', 'delivery_time', 'total_price']
    readonly_fields = ['sum_price', 'delivery_price', 'total_price']
    inlines = [OrderItemInline]


@staff_member_required
def custom_admin_index(request):
    # Earnings (monthly revenue)
    monthly_revenue = (
        Order.objects.filter(
            created_at__month=now().month,
            created_at__year=now().year
        ).aggregate(total=Sum('total_price'))['total'] or 0
    )

    # Orders count
    total_orders = Order.objects.count()
    new_orders = Order.objects.filter(
        created_at__gte=now() - timedelta(days=2)
    ).count()

    # Customers count
    total_customers = User.objects.count()
    new_customers = User.objects.filter(
        date_joined__gte=now() - timedelta(days=2)
    ).count()

    # Latest orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    current_year = now().year
    selected_year = int(request.GET.get('year', current_year))

    # Aggregate revenue by month
    orders = (
        Order.objects.filter(created_at__year=selected_year)
        .values_list('created_at__month')
        .annotate(total=Sum('total_price'))
    )

    # Create a full list of 12 months with default 0
    monthly_totals = [0] * 12
    for month, total in orders:
        monthly_totals[month - 1] = float(total or 0)


    category_totals = (
        OrderItem.objects
        .values(category=F('product__category'))
        .annotate(total_sales=Sum(F('price_at_order') * F('quantity')))
    )

    men_total = sum(item['total_sales'] for item in category_totals if item['category'] == 'men') or 0
    women_total = sum(item['total_sales'] for item in category_totals if item['category'] == 'women') or 0
    kids_total = sum(item['total_sales'] for item in category_totals if item['category'] == 'kids') or 0
    total_all = men_total + women_total + kids_total

    if total_all > 0:
        men_percent = (men_total / total_all) * 100
        women_percent = (women_total / total_all) * 100
        kids_percent = (kids_total / total_all) * 100
    else:
        men_percent = women_percent = kids_percent = 0



    context = {
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'new_orders': new_orders,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'recent_orders': recent_orders,
        "chart_labels": json.dumps(list(calendar.month_abbr)[1:]),
        "chart_data": json.dumps(monthly_totals),
        "selected_year": selected_year,
        "available_years": list(range(current_year, current_year - 5, -1)),
        "men_percent": men_percent,
        "women_percent": women_percent,
        "kids_percent": kids_percent,
        **admin.site.each_context(request),

    }

    return TemplateResponse(request, 'admin/index.html', context)




# Hook the custom index into admin
admin.site.index = custom_admin_index





