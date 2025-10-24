import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings')
django.setup()

from apps.main.models import Product

products = Product.objects.all()[:5]
print("\nCurrent Product Stock Levels:")
print("=" * 60)
for p in products:
    print(f"ID: {p.id:3d} | Name: {p.name:30s} | Stock: {p.stock:4d}")
print("=" * 60)
