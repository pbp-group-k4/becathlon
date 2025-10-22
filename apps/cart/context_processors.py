from .utils import get_or_create_cart

def cart_context(request):
    """
    Add cart and cart_item_count to all template contexts
    """
    cart = get_or_create_cart(request)
    return {
        'cart': cart,
        'cart_item_count': cart.get_total_items(),
    }