from .models import Cart

def get_or_create_cart(request):
    """
    Get existing cart or create new one for user/session
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def transfer_guest_cart_to_user(request):
    """
    Called after user login to merge guest cart into user cart
    """
    if not request.user.is_authenticated:
        return

    session_key = request.session.session_key
    if not session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=session_key)
        user_cart, created = Cart.objects.get_or_create(user=request.user)

        if guest_cart != user_cart:
            user_cart.merge_carts(guest_cart)
    except Cart.DoesNotExist:
        pass

def validate_cart_item_stock(product, requested_quantity):
    """
    Check if product has sufficient stock
    Returns (is_valid, error_message)
    """
    if product.stock < requested_quantity:
        return False, f"Only {product.stock} items available in stock."
    return True, None