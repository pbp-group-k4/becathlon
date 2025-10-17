"""
Script to populate initial product types for Becathlon
Run this with: python manage.py shell < seed_product_types.py
Or: python -c "exec(open('seed_product_types.py').read())"
"""

from apps.main.models import ProductType

# Define product types similar to Decathlon
product_types_data = [
    {"name": "Running", "description": "Running shoes, apparel, and accessories"},
    {"name": "Cycling", "description": "Bikes, cycling gear, and accessories"},
    {"name": "Swimming", "description": "Swimwear, goggles, and swimming equipment"},
    {"name": "Fitness", "description": "Gym equipment, weights, and fitness accessories"},
    {"name": "Team Sports", "description": "Equipment for football, basketball, volleyball, etc."},
    {"name": "Racket Sports", "description": "Tennis, badminton, squash equipment"},
    {"name": "Hiking", "description": "Hiking boots, backpacks, and outdoor gear"},
    {"name": "Camping", "description": "Tents, sleeping bags, and camping accessories"},
    {"name": "Water Sports", "description": "Kayaking, surfing, and water sports equipment"},
    {"name": "Winter Sports", "description": "Skiing, snowboarding, and winter gear"},
    {"name": "Yoga", "description": "Yoga mats, blocks, and accessories"},
    {"name": "Boxing", "description": "Boxing gloves, punching bags, and training gear"},
]

# Create product types
for pt_data in product_types_data:
    product_type, created = ProductType.objects.get_or_create(
        name=pt_data["name"],
        defaults={"description": pt_data["description"]}
    )
    if created:
        print(f"Created: {product_type.name}")
    else:
        print(f"Already exists: {product_type.name}")

print(f"\nTotal product types: {ProductType.objects.count()}")
