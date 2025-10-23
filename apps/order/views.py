from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
import logging
import re

from apps.cart.models import Cart, CartItem
from apps.cart.utils import get_or_create_cart, validate_cart_item_stock
from apps.main.models import Product
from .models import Order, OrderItem, ShippingAddress, Payment

logger = logging.getLogger(__name__)


def validate_shipping_address_data(post_data):
    """
    Validate shipping address form data.
    Returns (is_valid, errors_dict)
    """
    errors = {}
    
    # Validate full name
    full_name = post_data.get('full_name', '').strip()
    if not full_name:
        errors['full_name'] = "Full name is required."
    elif len(full_name) < 3:
        errors['full_name'] = "Full name must be at least 3 characters."
    elif len(full_name) > 100:
        errors['full_name'] = "Full name must not exceed 100 characters."
    
    # Validate phone number
    phone_number = post_data.get('phone_number', '').strip()
    if not phone_number:
        errors['phone_number'] = "Phone number is required."
    elif not re.match(r'^[\d\s\-\+\(\)]{7,20}$', phone_number):
        errors['phone_number'] = "Phone number format is invalid."
    
    # Validate address line 1
    address_line1 = post_data.get('address_line1', '').strip()
    if not address_line1:
        errors['address_line1'] = "Address is required."
    elif len(address_line1) < 5:
        errors['address_line1'] = "Address must be at least 5 characters."
    elif len(address_line1) > 255:
        errors['address_line1'] = "Address must not exceed 255 characters."
    
    # Validate city
    city = post_data.get('city', '').strip()
    if not city:
        errors['city'] = "City is required."
    elif len(city) < 2:
        errors['city'] = "City must be at least 2 characters."
    elif len(city) > 100:
        errors['city'] = "City must not exceed 100 characters."
    
    # Validate postal code
    postal_code = post_data.get('postal_code', '').strip()
    if not postal_code:
        errors['postal_code'] = "Postal code is required."
    elif not re.match(r'^[\d\s\-]{4,20}$', postal_code):
        errors['postal_code'] = "Postal code format is invalid."
    
    # Validate country
    valid_countries = ['Indonesia', 'Malaysia', 'Singapore', 'Thailand', 'Philippines']
    country = post_data.get('country', '').strip()
    if not country:
        errors['country'] = "Country is required."
    elif country not in valid_countries:
        errors['country'] = f"Invalid country. Choose from: {', '.join(valid_countries)}"
    
    # Optional: address line 2 (just length check)
    address_line2 = post_data.get('address_line2', '').strip()
    if address_line2 and len(address_line2) > 255:
        errors['address_line2'] = "Address line 2 must not exceed 255 characters."
    
    # Optional: state/province (just length check)
    state = post_data.get('state', '').strip()
    if state and len(state) > 100:
        errors['state'] = "State/Province must not exceed 100 characters."
    
    return len(errors) == 0, errors


def validate_payment_method(payment_method):
    """
    Validate payment method is one of the allowed choices.
    Returns (is_valid, error_message)
    """
    valid_methods = ['CREDIT_CARD', 'BANK_TRANSFER', 'E_WALLET', 'COD']
    if not payment_method or payment_method not in valid_methods:
        return False, f"Invalid payment method. Choose from: {', '.join(valid_methods)}"
    return True, None


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
    Process the checkout form submission with full validation.
    """
    # Validate shipping address
    is_valid, errors = validate_shipping_address_data(request.POST)
    if not is_valid:
        for field, error_msg in errors.items():
            messages.error(request, f"{field}: {error_msg}")
        logger.warning(f"Checkout validation failed for user {request.user.id}: {errors}")
        return redirect('order:checkout')
    
    # Validate payment method
    payment_method = request.POST.get('payment_method', '').strip()
    is_valid, error_msg = validate_payment_method(payment_method)
    if not is_valid:
        messages.error(request, error_msg)
        logger.warning(f"Invalid payment method for user {request.user.id}: {payment_method}")
        return redirect('order:checkout')
    
    # Re-validate cart items stock (in case items were purchased by others)
    try:
        for item in cart_items:
            is_valid, error_msg = validate_cart_item_stock(item.product, item.quantity)
            if not is_valid:
                messages.error(request, f"{item.product.name}: {error_msg}")
                logger.warning(f"Stock validation failed for user {request.user.id}: {item.product.id}")
                return redirect('order:checkout')
    except Exception as e:
        messages.error(request, "Error validating stock. Please try again.")
        logger.error(f"Stock validation error for user {request.user.id}: {str(e)}")
        return redirect('order:checkout')
    
    try:
        # Create shipping address
        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name').strip(),
            phone_number=request.POST.get('phone_number').strip(),
            address_line1=request.POST.get('address_line1').strip(),
            address_line2=request.POST.get('address_line2', '').strip(),
            city=request.POST.get('city').strip(),
            state=request.POST.get('state', '').strip(),
            postal_code=request.POST.get('postal_code').strip(),
            country=request.POST.get('country', 'Indonesia').strip(),
        )

        # Create order using the create_from_cart method
        order = Order.create_from_cart(
            cart=cart,
            shipping_address=shipping_address
        )

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            method=payment_method,
            amount=order.total_price,
            status='SUCCESS'  # Mock successful payment
        )

        # Update order status to PAID since payment was successful
        order.status = Order.Status.PAID
        order.save()

        logger.info(f"Order #{order.id} created successfully for user {request.user.id}")
        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('order:checkout_success', order_id=order.id)

    except ShippingAddress.DoesNotExist as e:
        messages.error(request, "Error creating shipping address. Please try again.")
        logger.error(f"Shipping address creation error for user {request.user.id}: {str(e)}")
        return redirect('order:checkout')
    except Exception as e:
        messages.error(request, "Error processing checkout. Please try again.")
        logger.error(f"Checkout processing error for user {request.user.id}: {str(e)}", exc_info=True)
        return redirect('order:checkout')


@login_required
def checkout_success(request, order_id):
    """
    Display checkout success page.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order/checkout_success.html', context)


@login_required
def order_list(request):
    """
    Display all orders for the logged-in user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'order/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """
    Display detailed view of a specific order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order/order_detail.html', context)
