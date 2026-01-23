from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decimal import Decimal
from .models import Product, ProductVariant, Cart, CartItem, Order, OrderItem
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_cart(request):
    """Get or create a cart for the current user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def shop_home(request):
    """Display all active products"""
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
    }
    return render(request, 'shop/shop_home.html', context)


def product_detail(request, product_id):
    """Display individual product with variants"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    variants = product.variants.filter(in_stock=True)
    
    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'shop/product_detail.html', context)


def view_cart(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request)
    
    context = {
        'cart': cart,
    }
    return render(request, 'shop/cart.html', context)


def add_to_cart(request, variant_id):
    """Add a product variant to cart"""
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, id=variant_id, in_stock=True)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{variant.product.name} added to cart!')
        return redirect('shop:view_cart')
    
    return redirect('shop:home')


def update_cart_item(request, item_id):
    """Update quantity of cart item"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = get_or_create_cart(request)
        
        # Verify this item belongs to the current cart
        if cart_item.cart == cart:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated!')
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart!')
        
    return redirect('shop:view_cart')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Verify this item belongs to the current cart
    if cart_item.cart == cart:
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
    
    return redirect('shop:view_cart')


def checkout(request):
    """Checkout page with Stripe integration"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:home')
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')
        customer_notes = request.POST.get('customer_notes', '')
        
        # Calculate totals
        # Calculate totals
        subtotal = cart.get_total()
        shipping_cost = Decimal('8.00')  # Flat rate for now
        tax = Decimal('0')  # Calculate based on state if needed
        total_amount = subtotal + shipping_cost + tax
        
        try:
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(total_amount * 100),  # Stripe uses cents
                        'product_data': {
                            'name': 'Watercolors By Karla - Art Print Order',
                            'description': f'Order for {first_name} {last_name}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/shop/checkout/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/shop/checkout/'),
                metadata={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'address_line_2': address_line_2,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                    'country': country,
                    'customer_notes': customer_notes,
                    'cart_id': str(cart.id),
                    'subtotal': str(subtotal),
                    'shipping_cost': str(shipping_cost),
                    'tax': str(tax),
                }
            )
            
            return redirect(checkout_session.url)
            
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('shop:checkout')
    
    # Calculate shipping and total for display
    subtotal = cart.get_total()
    shipping_cost = Decimal('8.00')  # Flat rate for now
    tax = Decimal('0')  # Calculate based on state if needed
    total = subtotal + shipping_cost + tax
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'shop/checkout.html', context)


def checkout_success(request):
    """Handle successful checkout"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid checkout session.')
        return redirect('shop:home')
    
    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Get metadata
        metadata = checkout_session.metadata
        cart = Cart.objects.get(id=metadata['cart_id'])
        
        # Create the order
        order = Order.objects.create(
            email=metadata['email'],
            first_name=metadata['first_name'],
            last_name=metadata['last_name'],
            phone=metadata.get('phone', ''),
            address=metadata['address'],
            address_line_2=metadata.get('address_line_2', ''),
            city=metadata['city'],
            state=metadata['state'],
            zip_code=metadata['zip_code'],
            country=metadata['country'],
            stripe_payment_intent=checkout_session.payment_intent,
            status='paid',
            subtotal=metadata['subtotal'],
            shipping_cost=metadata['shipping_cost'],
            tax=metadata['tax'],
            total_amount=checkout_session.amount_total / 100,  # Convert from cents
            customer_notes=metadata.get('customer_notes', ''),
        )
        
        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=cart_item.variant,
                product_name=cart_item.variant.product.name,
                variant_size=cart_item.variant.size,
                variant_paper_type=cart_item.variant.paper_type,
                quantity=cart_item.quantity,
                price=cart_item.variant.price,
            )
        
        # Send confirmation email to customer
        send_order_confirmation_email(order)
        
        # Send notification email to Karla
        send_order_notification_to_admin(order)
        
        # Clear the cart
        cart.items.all().delete()
        cart.delete()
        
        # Redirect to order confirmation
        return redirect('shop:order_confirmation', order_number=order.order_number)
        
    except Exception as e:
        messages.error(request, f'Error processing order: {str(e)}')
        return redirect('shop:home')


def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_confirmation.html', context)


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - {order.order_number}'
    
    # Create email body
    message = f"""
    Thank you for your order!
    
    Order Number: {order.order_number}
    Total: ${order.total_amount}
    
    We'll send you another email when your order ships.
    
    Order Details:
    """
    
    for item in order.items.all():
        message += f"\n- {item.product_name} ({item.variant_size}) x{item.quantity} - ${item.get_subtotal()}"
    
    message += f"""
    
    Shipping Address:
    {order.get_shipping_address()}
    
    Questions? Email us at WatercolorsbyKarla@gmail.com
    
    Thank you!
    Watercolors By Karla
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending customer email: {e}")


def send_order_notification_to_admin(order):
    """Send order notification to Karla"""
    subject = f'New Order Received - {order.order_number}'
    
    message = f"""
    NEW ORDER RECEIVED!
    
    Order Number: {order.order_number}
    Customer: {order.get_full_name()}
    Email: {order.email}
    Phone: {order.phone}
    
    Order Details:
    """
    
    for item in order.items.all():
        message += f"\n- {item.product_name} ({item.variant_size} - {item.variant_paper_type}) x{item.quantity} - ${item.get_subtotal()}"
    
    message += f"""
    
    Subtotal: ${order.subtotal}
    Shipping: ${order.shipping_cost}
    Tax: ${order.tax}
    TOTAL: ${order.total_amount}
    
    Shipping Address:
    {order.get_shipping_address()}
    
    Customer Notes:
    {order.customer_notes if order.customer_notes else 'None'}
    
    View in admin: http://127.0.0.1:8000/admin/shop/order/{order.id}/change/
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['WatercolorsbyKarla@gmail.com'],  # Karla's email
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending admin email: {e}")