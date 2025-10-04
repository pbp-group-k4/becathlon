from decimal import Decimal

from django.shortcuts import render
from django.utils import timezone

from .models import Category, Product


def _serialize_product(product):
    return {
        'name': product.get('name'),
        'category': product.get('category', 'Multi-sport'),
        'description': product.get('description', ''),
        'price': product.get('price', Decimal('0.00')),
        'image': product.get('image'),
        'created_at': product.get('created_at', timezone.now()),
    }


def _build_product_card(product, meta):
    base = _serialize_product(product)
    base.update({
        'rating': meta.get('rating', 4.7),
        'reviews': meta.get('reviews', 64),
        'vendor': meta.get('vendor', 'Becathlon Collective'),
        'badge': meta.get('badge'),
        'options': meta.get('options', ['Add to cart', 'Choose options']),
        'is_new': meta.get('is_new', False),
        'is_on_sale': meta.get('is_on_sale', False),
        'discount': meta.get('discount'),
    })
    return base


def home(request):
    """Render the Becathlon landing page with structured merchandising data."""

    categories = Category.objects.prefetch_related('products').order_by('name')
    category_counts = {category.name.lower(): category.products.count() for category in categories}

    product_queryset = Product.objects.select_related('category').order_by('-created_at')
    product_payloads = [
        {
            'name': product.name,
            'category': product.category.name if product.category_id else 'Multi-sport',
            'description': product.description,
            'price': product.price,
            'image': product.image.url if product.image else None,
            'created_at': product.created_at,
        }
        for product in product_queryset
    ]

    if not product_payloads:
        now = timezone.localtime()
        product_payloads = [
            {
                'name': 'Summit Trail Backpack 55L',
                'category': 'Backpacking',
                'description': 'Streamlined suspension and weatherproof storage for multi-day hikes.',
                'price': Decimal('189.00'),
                'image': None,
                'created_at': now,
            },
            {
                'name': 'Glacier Ridge Insulated Jacket',
                'category': 'Snow & Ski',
                'description': 'PrimaLoft warmth and breathable panels keep you primed for steep descents.',
                'price': Decimal('229.00'),
                'image': None,
                'created_at': now,
            },
            {
                'name': 'StrideFlex Tempo Shoes',
                'category': 'Running',
                'description': 'Responsive cushioning and trail-ready grip for mixed terrain tempo days.',
                'price': Decimal('129.00'),
                'image': None,
                'created_at': now,
            },
            {
                'name': 'Trailhead Titanium Poles',
                'category': 'Hiking',
                'description': 'Featherweight stability with rapid-lock adjustments for any elevation.',
                'price': Decimal('99.00'),
                'image': None,
                'created_at': now,
            },
            {
                'name': 'Overland Expedition Tent',
                'category': 'Camping',
                'description': 'Four-season shelter with color-coded setup for weekend crews.',
                'price': Decimal('369.00'),
                'image': None,
                'created_at': now,
            },
        ]

    popular_meta = [
        {'rating': 4.9, 'reviews': 284, 'vendor': 'Summit Syndicate', 'badge': 'Top Rated', 'options': ['Add to cart', 'Quick view'], 'is_on_sale': True, 'discount': 'Save 15%'},
        {'rating': 4.8, 'reviews': 190, 'vendor': 'Altitude Outfitters', 'badge': 'Trending', 'options': ['Add to cart', 'Choose options']},
        {'rating': 4.9, 'reviews': 321, 'vendor': 'North River Co.', 'badge': 'Staff pick', 'options': ['Add to cart', 'View details']},
        {'rating': 4.7, 'reviews': 156, 'vendor': 'Evertrail Collective', 'options': ['Add to cart', 'Compare']},
        {'rating': 4.8, 'reviews': 208, 'vendor': 'Arcadian Gear Lab', 'badge': 'Limited', 'options': ['Add to cart', 'Choose size']},
        {'rating': 5.0, 'reviews': 412, 'vendor': 'Becathlon Labs', 'badge': 'Pro approved', 'options': ['Add to cart', 'Customize'], 'is_on_sale': True, 'discount': 'Bundle & save'},
    ]

    new_arrival_meta = [
        {'rating': 4.8, 'reviews': 86, 'vendor': 'Trail & Co.', 'is_new': True, 'options': ['Add to cart', 'See details']},
        {'rating': 4.7, 'reviews': 64, 'vendor': 'Peak Collective', 'is_new': True, 'options': ['Add to cart', 'Quick view']},
        {'rating': 4.9, 'reviews': 142, 'vendor': 'Bivouac Works', 'is_new': True, 'options': ['Add to cart', 'Choose options']},
        {'rating': 4.6, 'reviews': 58, 'vendor': 'CycleFrontier', 'is_new': True, 'options': ['Add to cart', 'Build kit']},
    ]

    popular_products = [
        _build_product_card(product_payloads[index], popular_meta[index % len(popular_meta)])
        for index in range(min(6, len(product_payloads)))
    ]

    arrival_source = product_payloads[1:] + product_payloads[:1]
    new_arrivals = [
        _build_product_card(arrival_source[index], new_arrival_meta[index % len(new_arrival_meta)])
        for index in range(min(4, len(arrival_source)))
    ]

    sport_highlights = [
        {
            'id': 'sport-hiking',
            'name': 'Hiking',
            'summary': 'Layer smart and stay agile with breathable shells, moisture-wicking base layers, and trail traction.',
            'stat': f"{category_counts.get('hiking', '24')} curated picks",
        },
        {
            'id': 'sport-backpacking',
            'name': 'Backpacking',
            'summary': 'Dial in multi-day packs with modular storage, titanium cook systems, and recovery tools.',
            'stat': f"{category_counts.get('backpacking', '18')} weekend-ready kits",
        },
        {
            'id': 'sport-camping',
            'name': 'Camping',
            'summary': 'Basecamp comfort featuring weatherproof shelters, elevated sleep systems, and communal cookware.',
            'stat': f"{category_counts.get('camping', '32')} comfort upgrades",
        },
        {
            'id': 'sport-snow',
            'name': 'Snow & Ski',
            'summary': 'Ride insulated, articulated layers paired with avalanche-ready safety tech and tuning tools.',
            'stat': f"{category_counts.get('snow & ski', '14')} cold-front essentials",
        },
        {
            'id': 'sport-running',
            'name': 'Running',
            'summary': 'From tempo flats to recovery boots, equip every mile with endurance-first design.',
            'stat': f"{category_counts.get('running', '28')} road & trail picks",
        },
        {
            'id': 'sport-cycling',
            'name': 'Cycling',
            'summary': 'Aero layers, safety tech, and maintenance kits engineered for urban loops to alpine passes.',
            'stat': f"{category_counts.get('cycling', '22')} ride upgrades",
        },
    ]

    hero_category_links = [
        {'label': 'Hiking', 'anchor': '#sport-hiking'},
        {'label': 'Backpacking', 'anchor': '#sport-backpacking'},
        {'label': 'Camping', 'anchor': '#sport-camping'},
        {'label': 'Snow & Ski', 'anchor': '#sport-snow'},
        {'label': 'Running', 'anchor': '#sport-running'},
        {'label': 'Cycling', 'anchor': '#sport-cycling'},
    ]

    highlight_sections = [
        {
            'title': 'High-Performance Products For Everyone',
            'subtitle': 'Engineered to adapt from first hikes to summit pushes with inclusive sizing and modular fit.',
            'theme': 'dark',
            'products': popular_products[:2],
        },
        {
            'title': 'Trending Now',
            'subtitle': 'Real-time community favorites refreshed every 24 hours.',
            'theme': 'light',
            'products': new_arrivals[:2] or popular_products[2:4],
        },
        {
            'title': 'Adventure Ready',
            'subtitle': 'Durable gear packs for backcountry missions and quick Thursday night escape plans.',
            'theme': 'accent',
            'products': popular_products[3:5] or popular_products[:2],
        },
        {
            'title': 'Staff Pick',
            'subtitle': 'Hand-selected essentials validated by the Becathlon field team.',
            'theme': 'outline',
            'products': popular_products[4:6] or new_arrivals[:2],
        },
    ]

    context = {
        'announcement': 'Free Shipping Over $49 — Extended Weekend Window',
        'sport_highlights': sport_highlights,
        'hero_category_links': hero_category_links,
        'popular_products': popular_products,
        'new_arrivals': new_arrivals,
        'highlight_sections': highlight_sections,
    }

    return render(request, 'main/home.html', context)
