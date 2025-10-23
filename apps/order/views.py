from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from apps.cart.models import Cart, CartItem
from apps.cart.utils import get_or_create_cart
from apps.main.models import Product
from .models import Order, OrderItem, ShippingAddress, Payment


@login_required
def checkout_view(request):
    """
    Checkout view - displays checkout form and processes orders.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')
    
    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('catalog:home')

    if request.method == 'POST':
        return process_checkout(request, cart, cart_items)
    
    # GET request - display checkout form
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'order/checkout.html', context)


@transaction.atomic
def process_checkout(request, cart, cart_items):
    """
    Process the checkout form submission.
    """
    try:
        # Create shipping address
        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            address_line1=request.POST.get('address_line1'),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state', ''),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country', 'Indonesia'),
        )

        # Create order using the create_from_cart method
        order = Order.create_from_cart(
            cart=cart,
            shipping_address=shipping_address
        )

        # Create payment record
        payment_method = request.POST.get('payment_method', 'CREDIT_CARD')
        payment = Payment.objects.create(
            order=order,
            method=payment_method,
            amount=order.total_price,
            status='SUCCESS'  # Mock successful payment
        )

        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('order:checkout_success', order_id=order.id)

    except Exception as e:
        messages.error(request, f"Error processing checkout: {str(e)}")
        return redirect('order:checkout')


def checkout_success(request, order_id):
    """
    Display checkout success page.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order/checkout_success.html', context)
