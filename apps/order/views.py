from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
import logging
import re
import json

from apps.cart.models import Cart, CartItem
from apps.cart.utils import get_or_create_cart, validate_cart_item_stock
from apps.main.models import Product
from .models import Order, OrderItem, ShippingAddress, Payment, ProductRating

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


class CheckoutResult:
    """Result object for checkout service operations."""
    def __init__(self, success, order=None, error_type=None, error_message=None, errors=None):
        self.success = success
        self.order = order
        self.error_type = error_type  # 'validation', 'stock', 'processing'
        self.error_message = error_message
        self.errors = errors or {}  # Field-level validation errors


@transaction.atomic
def process_checkout_service(user, cart, cart_items, shipping_data, payment_method):
    """
    Core checkout business logic - creates order from cart with shipping and payment.

    Args:
        user: The authenticated user
        cart: The user's cart
        cart_items: QuerySet of cart items
        shipping_data: Dict with shipping address fields
        payment_method: Payment method string (e.g., 'CREDIT_CARD')

    Returns:
        CheckoutResult with success status and order or error details
    """
    # Validate shipping address
    is_valid, errors = validate_shipping_address_data(shipping_data)
    if not is_valid:
        return CheckoutResult(
            success=False,
            error_type='validation',
            error_message='Shipping address validation failed',
            errors=errors
        )

    # Validate payment method
    is_valid, error_msg = validate_payment_method(payment_method)
    if not is_valid:
        return CheckoutResult(
            success=False,
            error_type='validation',
            error_message=error_msg
        )

    # Validate cart items stock
    for item in cart_items:
        is_valid, error_msg = validate_cart_item_stock(item.product, item.quantity)
        if not is_valid:
            return CheckoutResult(
                success=False,
                error_type='stock',
                error_message=f"{item.product.name}: {error_msg}"
            )

    try:
        # Create shipping address
        shipping_address = ShippingAddress.objects.create(
            user=user,
            full_name=shipping_data.get('full_name', '').strip(),
            phone_number=shipping_data.get('phone_number', '').strip(),
            address_line1=shipping_data.get('address_line1', '').strip(),
            address_line2=shipping_data.get('address_line2', '').strip(),
            city=shipping_data.get('city', '').strip(),
            state=shipping_data.get('state', '').strip(),
            postal_code=shipping_data.get('postal_code', '').strip(),
            country=shipping_data.get('country', 'Indonesia').strip(),
        )

        # Create order using the create_from_cart method
        # This will automatically decrement stock atomically
        order = Order.create_from_cart(
            cart=cart,
            shipping_address=shipping_address
        )

        # Create payment record
        Payment.objects.create(
            order=order,
            method=payment_method,
            amount=order.total_price,
            status='SUCCESS'  # Mock successful payment
        )

        # Update order status to PAID and start delivery tracking
        order.status = Order.Status.PAID
        order.start_delivery_tracking()
        order.save()

        logger.info(f"Order #{order.id} created successfully for user {user.id}")
        return CheckoutResult(success=True, order=order)

    except ValueError as e:
        # Handle insufficient stock error from Order.create_from_cart
        return CheckoutResult(
            success=False,
            error_type='stock',
            error_message=str(e)
        )
    except Exception as e:
        logger.error(f"Checkout processing error for user {user.id}: {str(e)}", exc_info=True)
        return CheckoutResult(
            success=False,
            error_type='processing',
            error_message='Error processing checkout. Please try again.'
        )


def checkout_view(request):
    """
    Checkout view - displays checkout form and processes orders.
    Requires authentication - redirects to login if guest.
    """
    if not request.user.is_authenticated:
        login_url = f"{reverse('auth:login')}?{urlencode({'next': reverse('order:checkout')})}"
        messages.info(request, 'Please log in to proceed to checkout.')
        return redirect(login_url)
    
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


def process_checkout(request, cart, cart_items):
    """
    Process the checkout form submission with full validation.
    Uses the shared checkout service for business logic.
    """
    # Extract shipping data from POST
    shipping_data = {
        'full_name': request.POST.get('full_name', ''),
        'phone_number': request.POST.get('phone_number', ''),
        'address_line1': request.POST.get('address_line1', ''),
        'address_line2': request.POST.get('address_line2', ''),
        'city': request.POST.get('city', ''),
        'state': request.POST.get('state', ''),
        'postal_code': request.POST.get('postal_code', ''),
        'country': request.POST.get('country', 'Indonesia'),
    }
    payment_method = request.POST.get('payment_method', '').strip()

    # Use the shared checkout service
    result = process_checkout_service(
        user=request.user,
        cart=cart,
        cart_items=cart_items,
        shipping_data=shipping_data,
        payment_method=payment_method
    )

    if result.success:
        messages.success(request, f"Order #{result.order.id} created successfully!")
        return redirect('order:checkout_success', order_id=result.order.id)
    else:
        # Handle validation errors with field-level messages
        if result.errors:
            for field, error_msg in result.errors.items():
                messages.error(request, f"{field}: {error_msg}")
            logger.warning(f"Checkout validation failed for user {request.user.id}: {result.errors}")
        else:
            messages.error(request, result.error_message)
            if result.error_type == 'stock':
                logger.warning(f"Stock validation failed for user {request.user.id}: {result.error_message}")
            else:
                logger.warning(f"Checkout failed for user {request.user.id}: {result.error_message}")
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
    
    # Update delivery status for all orders before displaying
    for order in orders:
        if order.delivery_started_at:
            order.update_delivery_status()
    
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
    
    # Update delivery status before displaying
    order.update_delivery_status()
    
    # Get rated products for this order
    rated_product_ids = order.product_ratings.values_list('product_id', flat=True)
    
    context = {
        'order': order,
        'rated_product_ids': list(rated_product_ids),
    }
    return render(request, 'order/order_detail.html', context)


@login_required
def check_delivery_status(request, order_id):
    """
    AJAX endpoint to check current delivery status of an order.
    Returns JSON with current status, progress percentage, and time remaining.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Update and get current status
    order.update_delivery_status()
    current_status, seconds_remaining = order.get_current_delivery_status()
    progress = order.get_delivery_progress_percentage()
    
    # Get rated products
    rated_product_ids = list(order.product_ratings.values_list('product_id', flat=True))
    
    return JsonResponse({
        'success': True,
        'delivery_status': current_status,
        'delivery_status_display': order.get_delivery_status_display(),
        'progress_percentage': progress,
        'seconds_remaining': seconds_remaining,
        'is_delivered': current_status == Order.DeliveryStatus.DELIVERED,
        'rated_product_ids': rated_product_ids,
    })


@login_required
def submit_rating(request, order_id):
    """
    AJAX endpoint to submit a product rating.
    Expects POST data: product_id, rating (1-5), review (optional)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is delivered
    if order.delivery_status != Order.DeliveryStatus.DELIVERED:
        return JsonResponse({
            'success': False, 
            'error': 'Can only rate products after delivery'
        }, status=400)
    
    try:
        product_id = int(request.POST.get('product_id'))
        rating_value = int(request.POST.get('rating'))
        review_text = request.POST.get('review', '').strip()
        
        # Validate rating
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({
                'success': False, 
                'error': 'Rating must be between 1 and 5'
            }, status=400)
        
        # Verify product is in this order
        product = get_object_or_404(Product, id=product_id)
        if not order.items.filter(product=product).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Product not in this order'
            }, status=400)
        
        # Create or update rating
        from .models import ProductRating
        rating_obj, created = ProductRating.objects.update_or_create(
            user=request.user,
            product=product,
            order=order,
            defaults={
                'rating': rating_value,
                'review': review_text,
            }
        )
        
        # Update product aggregate rating
        product.update_aggregate_rating()
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted successfully!',
            'product_id': product_id,
            'new_aggregate_rating': float(product.rating),
        })
        
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False, 
            'error': 'Invalid data provided'
        }, status=400)
    except Exception as e:
        logger.error(f"Rating submission error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False, 
            'error': 'An error occurred while submitting your rating'
        }, status=500)


# ---------------------------------------------------------------------------
# Flutter Mobile API Views
# ---------------------------------------------------------------------------

@csrf_exempt
def flutter_checkout(request):
    """
    Handle checkout for Flutter app - accepts JSON body.
    Uses the shared checkout service for business logic.
    """
    if request.method != 'POST':
        return JsonResponse({'status': False, 'message': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'User not authenticated'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': False, 'message': 'Invalid JSON'}, status=400)

    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        return JsonResponse({'status': False, 'message': 'Cart is empty'}, status=400)

    # Extract payment method from JSON data
    payment_method = data.get('payment_method', '').strip()

    # Use the shared checkout service
    result = process_checkout_service(
        user=request.user,
        cart=cart,
        cart_items=cart_items,
        shipping_data=data,
        payment_method=payment_method
    )

    if result.success:
        return JsonResponse({
            'status': True,
            'message': 'Order created successfully',
            'order_id': result.order.id
        }, status=201)
    else:
        # Determine appropriate status code
        if result.error_type == 'validation':
            status_code = 400
        elif result.error_type == 'stock':
            status_code = 400
        else:
            status_code = 500

        response_data = {'status': False, 'message': result.error_message}
        if result.errors:
            response_data['errors'] = result.errors
        return JsonResponse(response_data, status=status_code)


@csrf_exempt
def flutter_order_list(request):
    """
    Return list of orders for the authenticated user in JSON format.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'User not authenticated'}, status=401)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    data = []
    for order in orders:
        # Update delivery status
        if order.delivery_started_at:
            order.update_delivery_status()
            
        data.append({
            'id': order.id,
            'status': order.status,
            'delivery_status': order.delivery_status,
            'delivery_status_display': order.get_delivery_status_display(),
            'total_price': float(order.total_price),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'item_count': order.get_item_count(),
        })

    return JsonResponse({'status': True, 'orders': data}, status=200)


@csrf_exempt
def flutter_order_detail(request, order_id):
    """
    Return detailed order info in JSON format.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'User not authenticated'}, status=401)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Order not found'}, status=404)

    order.update_delivery_status()
    
    items_data = []
    for item in order.items.select_related('product').all():
        items_data.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'subtotal': float(item.subtotal),
            # Use Product.get_primary_image_url() helper to avoid AttributeError
            'image_url': item.product.get_primary_image_url(),
        })

    shipping_data = {
        'full_name': order.shipping_address.full_name,
        'phone_number': order.shipping_address.phone_number,
        'address': f"{order.shipping_address.address_line1}, {order.shipping_address.city}, {order.shipping_address.postal_code}, {order.shipping_address.country}",
    }

    return JsonResponse({
        'status': True,
        'order': {
            'id': order.id,
            'status': order.status,
            'delivery_status': order.delivery_status,
            'delivery_status_display': order.get_delivery_status_display(),
            'total_price': float(order.total_price),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_data,
            'shipping_address': shipping_data,
            'rated_product_ids': list(order.product_ratings.values_list('product_id', flat=True))
        }
    }, status=200)


@csrf_exempt
def flutter_check_delivery_status(request, order_id):
    """
    Check delivery status for Flutter app.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'User not authenticated'}, status=401)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Order not found'}, status=404)
    
    order.update_delivery_status()
    current_status, seconds_remaining = order.get_current_delivery_status()
    progress = order.get_delivery_progress_percentage()
    
    return JsonResponse({
        'status': True,
        'delivery_status': current_status,
        'delivery_status_display': order.get_delivery_status_display(),
        'progress_percentage': progress,
        'seconds_remaining': seconds_remaining,
        'is_delivered': current_status == Order.DeliveryStatus.DELIVERED,
    }, status=200)


@csrf_exempt
def flutter_submit_rating(request, order_id):
    """
    Submit rating for Flutter app.
    """
    if request.method != 'POST':
        return JsonResponse({'status': False, 'message': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'User not authenticated'}, status=401)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Order not found'}, status=404)

    # Check if order is delivered
    if order.delivery_status != Order.DeliveryStatus.DELIVERED:
        return JsonResponse({
            'status': False, 
            'message': 'Can only rate products after delivery'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        product_id = int(data.get('product_id'))
        rating_value = int(data.get('rating'))
        review_text = data.get('review', '').strip()
        
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({'status': False, 'message': 'Rating must be between 1 and 5'}, status=400)
            
        # Verify product
        product = get_object_or_404(Product, id=product_id)
        if not order.items.filter(product=product).exists():
            return JsonResponse({'status': False, 'message': 'Product not in this order'}, status=400)

        # Create/Update rating
        rating_obj, created = ProductRating.objects.update_or_create(
            user=request.user,
            product=product,
            order=order,
            defaults={
                'rating': rating_value,
                'review': review_text,
            }
        )
        
        product.update_aggregate_rating()
        
        return JsonResponse({
            'status': True,
            'message': 'Rating submitted successfully!',
            'new_aggregate_rating': float(product.rating)
        }, status=200)

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': False, 'message': 'Invalid data provided'}, status=400)
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)}, status=500)
