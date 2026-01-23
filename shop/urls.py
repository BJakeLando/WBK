from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Product pages
    path('', views.shop_home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('order/confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
]