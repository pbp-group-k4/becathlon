from django.shortcuts import render, get_object_or_404
from apps.main.models import Product

def recommendations_for_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Simple rule: recommend similar products of same type
    if getattr(product, 'product_type', None):
        recs = Product.objects.filter(product_type=product.product_type).exclude(id=product.id)[:6]
    else:
        recs = Product.objects.exclude(id=product.id)[:6]

    return render(request, 'recommendation/product_recommendations.html', {'recommendations': recs})


def recommendations_for_user(request):
    # Placeholder personalized recs
    recs = Product.objects.all().order_by('-created_at')[:20]
    return render(request, 'recommendation/user_recommendations.html', {'products': recs})
