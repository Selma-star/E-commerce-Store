from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import custom_admin_index

admin.site.index = custom_admin_index

urlpatterns = [
    path('', views.home_view, name='home'), 
    path('signup/', views.signup_view, name='signup'),  
    path('signin/', views.signin_view, name='signin'),
    path('forgot-password/', views.password_view, name='forgot-password'),
    path('logout/', views.logout_view, name='logout'),
    path('store/', views.store_list, name='store-list'),
    path('store/shop/', views.shop_grid, name='shop-grid'),
    path('Myaccount/orders/', views.user_orders_view, name='orders'),
    path('Myaccount/settings/', views.settings_view, name='settings'),
    path('Myaccount/address/', views.address_view, name='address'),
    path('Myaccount/notification/', views.notification_view, name='notification'),
    path('shop-checkout', views.checkout_view, name='shop-checkout'),
    path('grappelli/', include('grappelli.urls')),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path("cart/sidebar/", views.cart_sidebar_view, name="cart_sidebar"),
    path('place-order/', views.place_order, name='place_order'),
    path('checkout/confirm-order/', views.confirm_order, name='confirm_order'),
    #path('controler/', views.dashboard_view, name='controler'),
    path('admin/', admin.site.urls), 
]


