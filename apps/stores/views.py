from math import radians, sin, cos, asin, sqrt
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET
from .models import Store

def store_locator(request):
    return render(request, "stores/locator.html")

def store_detail(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    return render(request, "stores/store_detail.html", {"store": store})

def _haversine_km(lat1, lon1, lat2, lon2):
    """Distance in KM between two WGS84 points."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

@require_GET
def api_stores(request):
    """
    GET /stores/api/?q=jakarta&lat=-6.2&lng=106.8&radius=50
    Returns JSON list of stores. All params optional.
    """
    q = (request.GET.get("q") or "").strip()
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    radius = float(request.GET.get("radius") or 0)

    qs = Store.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(address__icontains=q) | Q(country__icontains=q))

    items = list(qs.values("id", "name", "address", "city", "country", "latitude", "longitude", "store_hours"))

    return JsonResponse({"results": items})
