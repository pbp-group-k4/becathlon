from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse
from apps.main.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart, validate_cart_item_stock
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt

def cart_view(request):
    """
    Display full cart with all items
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__product_type').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': cart.get_subtotal(),
        'total_items': cart.get_total_items(),
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    """
    POST endpoint to add product to cart (works for both guests and authenticated users)
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    # Get quantity from POST data, default to 1
    quantity = int(request.POST.get('quantity', 1))

    # Validate stock
    is_valid, error_msg = validate_cart_item_stock(product, quantity)
    if not is_valid:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('catalog:product_detail', product_id=product.id)

    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added {quantity} x {product.name} to cart',
            'cart_count': cart.get_total_items(),
            'cart_subtotal': float(cart.get_subtotal()),
        })

    messages.success(request, f'Added {quantity} x {product.name} to cart')
    return redirect('cart:cart_view')

@require_POST
def update_cart_item(request, item_id):
    """
    POST endpoint to update item quantity
    """
    # Get cart item with proper authorization
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=session_key)

    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        message = 'Item removed from cart'
    else:
        # Validate stock
        is_valid, error_msg = validate_cart_item_stock(cart_item.product, quantity)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error_msg})

        cart_item.quantity = quantity
        cart_item.save()
        message = 'Cart updated'

    cart = cart_item.cart if quantity > 0 else get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'message': message,
        'cart_count': cart.get_total_items(),
        'cart_subtotal': float(cart.get_subtotal()),
        'item_subtotal': float(cart_item.get_subtotal()) if quantity > 0 else 0,
    })

@require_POST
def remove_from_cart(request, item_id):
    """
    POST/DELETE endpoint to remove item completely
    """
    # Get cart item with proper authorization
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=session_key)

    cart_item.delete()
    cart = get_or_create_cart(request)

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': cart.get_total_items(),
        'cart_subtotal': float(cart.get_subtotal()),
    })

@require_POST
def clear_cart(request):
    """
    POST endpoint to empty entire cart
    """
    cart = get_or_create_cart(request)
    cart.clear()

    return JsonResponse({
        'success': True,
        'message': 'Cart cleared',
        'cart_count': 0,
        'cart_subtotal': 0,
    })

def api_cart_summary(request):
    """
    GET endpoint returning cart summary as JSON
    """
    cart = get_or_create_cart(request)
    items = []
    for item in cart.items.select_related('product').all():
        items.append({
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.product.price),
            'subtotal': float(item.get_subtotal()),
        })

    return JsonResponse({
        'total_items': cart.get_total_items(),
        'subtotal': float(cart.get_subtotal()),
        'item_count': cart.get_item_count(),
        'items': items,
    })

def api_cart_count(request):
    """
    Lightweight GET endpoint returning only item count
    """
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.get_total_items()})

def checkout_view(request):
    """
    Checkout view - requires authentication
    Redirects to login if guest, retains cart after login via transfer_guest_cart_to_user
    """
    if not request.user.is_authenticated:
        login_url = f"{reverse('auth:login')}?{urlencode({'next': reverse('order:checkout')})}"
        messages.info(request, 'Please log in to proceed to checkout.')
        return redirect(login_url)
    
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_view')
    
    # TODO: Implement checkout logic
    # For now, show placeholder
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'product__product_type').all(),
        'subtotal': cart.get_subtotal(),
    }
    
    messages.info(request, 'Checkout functionality coming soon!')
    return redirect('cart:cart_view')

# flutter endpoints for all cart logic, csrf_exempt 

@csrf_exempt
def flutter_cart_view(request):
    """
    Flutter API endpoint to get cart summary
    """
    cart = get_or_create_cart(request)
    items = []
    for item in cart.items.select_related('product').all():
        items.append({
            'id': item.id,
            'product_id': item.product.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.product.price),
            'subtotal': float(item.get_subtotal()),
        })

    return JsonResponse({
        'total_items': cart.get_total_items(),
        'subtotal': float(cart.get_subtotal()),
        'item_count': cart.get_item_count(),
        'items': items,
    })

@csrf_exempt
def flutter_add_to_cart(request, product_id):
    """
    Flutter API endpoint to add product to cart
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # mimic the add_to_cart logic here

    # validate stock
    is_valid, error_msg = validate_cart_item_stock(product, quantity)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error_msg})
    # TODO: flutter redirect to product detail if stock invalid

    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({'success': True, 'message': 'Item added to cart'})

@csrf_exempt
def flutter_update_cart_item(request, item_id):
    """
    Flutter API endpoint to update cart item quantity
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # mimic the update_cart_item logic here

    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=session_key)

    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        cart = get_or_create_cart(request)
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_count': cart.get_total_items(),
            'cart_subtotal': float(cart.get_subtotal()),
            'item_subtotal': 0,
        })

    is_valid, error_msg = validate_cart_item_stock(cart_item.product, quantity)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error_msg})

    cart_item.quantity = quantity
    cart_item.save()
    cart = cart_item.cart

    return JsonResponse({
        'success': True,
        'message': 'Cart updated',
        'cart_count': cart.get_total_items(),
        'cart_subtotal': float(cart.get_subtotal()),
        'item_subtotal': float(cart_item.get_subtotal()),
    })

@csrf_exempt
def flutter_remove_from_cart(request, item_id):
    """
    Flutter API endpoint to remove cart item
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # mimic the remove_from_cart logic here

    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=session_key)

    cart_item.delete()
    cart = get_or_create_cart(request)

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': cart.get_total_items(),
        'cart_subtotal': float(cart.get_subtotal()),
    })

@csrf_exempt
def flutter_clear_cart(request):
    """
    Flutter API endpoint to clear cart
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # mimic the clear_cart logic here

    cart = get_or_create_cart(request)
    cart.clear()

    return JsonResponse({
        'success': True,
        'message': 'Cart cleared',
        'cart_count': 0,
        'cart_subtotal': 0,
    })

@csrf_exempt
def flutter_cart_count(request):
    """
    Flutter API endpoint to get cart item count
    """
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.get_total_items()})

@csrf_exempt
def flutter_checkout_view(request):
    """
    Flutter API endpoint for checkout view
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required for checkout'})

    cart = get_or_create_cart(request)

    if not cart.items.exists():
        return JsonResponse({'success': False, 'error': 'Your cart is empty'})
    
