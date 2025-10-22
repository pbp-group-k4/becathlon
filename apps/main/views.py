from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Product, ProductType
from django.db.models import Q
from django.contrib.auth.models import User


# Create your views here.


def home(request):
    """Home page displaying all products"""
    products = Product.objects.all().select_related('product_type', 'created_by')
    product_types = ProductType.objects.all()
    context = {
        'products': products,
        'product_types': product_types,
    }
    return render(request, 'main/home.html', context)


@login_required
@require_http_methods(["POST"])
def add_product_ajax(request):
    """AJAX endpoint to add a product"""
    try:
        data = json.loads(request.body)
        
        product_type_id = data.get('product_type')
        product_type = get_object_or_404(ProductType, id=product_type_id)
        
        product = Product.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            product_type=product_type,
            stock=data.get('stock', 0),
            image_url=data.get('image_url', ''),
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'product_type': product.product_type.name,
                'stock': product.stock,
                'image_url': product.image_url,
                'created_by': product.created_by.username,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_product_ajax(request, product_id):
    """AJAX endpoint to delete a product"""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Only allow the creator to delete their own product
        if product.created_by != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You can only delete your own products'
            }, status=403)
        
        product.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_products_ajax(request):
    """AJAX endpoint to get filtered products"""
    products = Product.objects.all().select_related('product_type', 'created_by')

    q = request.GET.get('q')             # search keyword
    product_type = request.GET.get('type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if product_type:
        products = products.filter(product_type__id=product_type)
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    products_data = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': str(p.price),
        'product_type': p.product_type.name,
        'stock': p.stock,
        'image_url': p.image_url,
        'created_by': p.created_by.username,
        'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
        'can_delete': request.user.is_authenticated and p.created_by == request.user
    } for p in products]

    return JsonResponse({'success': True, 'products': products_data})


def product_detail(request, product_id):
    """Show product details (sensitive info hidden for guests)"""
    product = get_object_or_404(Product.objects.select_related('product_type', 'created_by'), id=product_id)
    customer = None

    # Try to find the seller’s Customer profile
    try:
        customer = product.created_by.customer
    except Exception:
        customer = None

    show_contact = request.user.is_authenticated

    context = {
        'product': product,
        'customer': customer,
        'show_contact': show_contact,
    }
    return render(request, 'main/product_detail.html', context)
