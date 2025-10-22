from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from apps.main.models import Product, ProductType
from .models import ProductImage
from .forms import ProductFilterForm


def catalog_home(request):
    """Display all products with filtering and pagination"""
    products = Product.objects.select_related('product_type', 'created_by').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))
    )
    
    # Get filter form
    filter_form = ProductFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        # Category filter
        categories = request.GET.getlist('categories')
        if categories:
            products = products.filter(product_type__id__in=categories)
        
        # Price range filter
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        # Stock filter
        if filter_form.cleaned_data.get('in_stock_only'):
            products = products.filter(stock__gt=0)
        
        # Search filter
        search = filter_form.cleaned_data.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Sorting
        sort_by = filter_form.cleaned_data.get('sort_by', 'newest')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        else:  # newest
            products = products.order_by('-created_at')
    
    # Get product counts per category
    product_types = ProductType.objects.all()
    category_counts = {}
    for pt in product_types:
        category_counts[pt.id] = Product.objects.filter(product_type=pt).count()
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'product_types': product_types,
        'category_counts': category_counts,
        'filter_form': filter_form,
        'total_count': paginator.count,
    }
    
    return render(request, 'catalog/catalog.html', context)


def category_products(request, category_id):
    """Display products filtered by category"""
    category = get_object_or_404(ProductType, id=category_id)
    
    products = Product.objects.filter(product_type=category).select_related(
        'product_type', 'created_by'
    ).prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))
    )
    
    # Get filter form
    filter_form = ProductFilterForm(request.GET)
    
    # Apply additional filters
    if filter_form.is_valid():
        # Price range filter
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        # Stock filter
        if filter_form.cleaned_data.get('in_stock_only'):
            products = products.filter(stock__gt=0)
        
        # Search filter
        search = filter_form.cleaned_data.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Sorting
        sort_by = filter_form.cleaned_data.get('sort_by', 'newest')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        else:  # newest
            products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Get all categories for sidebar
    product_types = ProductType.objects.all()
    
    context = {
        'products': products_page,
        'category': category,
        'product_types': product_types,
        'filter_form': filter_form,
        'total_count': paginator.count,
    }
    
    return render(request, 'catalog/category.html', context)


def product_detail(request, product_id):
    """Display detailed product information"""
    product = get_object_or_404(
        Product.objects.select_related('product_type', 'created_by').prefetch_related('images'),
        id=product_id
    )
    
    # Get related products (same category, exclude current product)
    related_products = Product.objects.filter(
        product_type=product.product_type
    ).exclude(
        id=product.id
    ).select_related('product_type').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))
    )[:4]
    
    # Get all images for this product
    product_images = product.images.all()
    
    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
    }
    
    return render(request, 'catalog/product_detail.html', context)


def api_filter_products(request):
    """AJAX endpoint for filtering products"""
    products = Product.objects.select_related('product_type').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))
    )
    
    # Category filter
    category_ids = request.GET.getlist('category_ids[]')
    if category_ids:
        products = products.filter(product_type__id__in=category_ids)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
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
    
    # Stock filter
    if request.GET.get('in_stock_only') == 'true':
        products = products.filter(stock__gt=0)
    
    # Search filter
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    paginator = Paginator(products, 20)
    
    try:
        products_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products_page = paginator.page(1)
    
    # Build JSON response
    products_data = []
    for product in products_page:
        primary_image = product.images.first()
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'product_type': product.product_type.name,
            'product_type_id': product.product_type.id,
            'stock': product.stock,
            'image_url': primary_image.image_url if primary_image else product.image_url,
            'url': f'/catalog/product/{product.id}/',
        })
    
    return JsonResponse({
        'products': products_data,
        'total_count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': products_page.number,
        'has_next': products_page.has_next(),
        'has_previous': products_page.has_previous(),
    })


def api_product_quick_view(request, product_id):
    """AJAX endpoint for product quick view"""
    try:
        product = Product.objects.select_related('product_type').prefetch_related('images').get(id=product_id)
        
        images = [img.image_url for img in product.images.all()]
        if not images and product.image_url:
            images = [product.image_url]
        
        data = {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'product_type': product.product_type.name,
            'description': product.description,
            'stock': product.stock,
            'images': images,
            'in_stock': product.stock > 0,
        }
        
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
