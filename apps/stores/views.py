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
    try:
        q = (request.GET.get("q") or "").strip()
        lat_str = request.GET.get("lat")
        lng_str = request.GET.get("lng")
        radius_str = request.GET.get("radius")
        
        # Validate lat/lng if provided
        lat = None
        lng = None
        radius = 0
        
        if lat_str:
            try:
                lat = float(lat_str)
                if not (-90 <= lat <= 90):
                    return JsonResponse({"error": "Latitude must be between -90 and 90"}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid latitude value"}, status=400)
        
        if lng_str:
            try:
                lng = float(lng_str)
                if not (-180 <= lng <= 180):
                    return JsonResponse({"error": "Longitude must be between -180 and 180"}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid longitude value"}, status=400)
        
        if radius_str:
            try:
                radius = float(radius_str)
                if radius < 0:
                    return JsonResponse({"error": "Radius must be non-negative"}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid radius value"}, status=400)

        qs = Store.objects.filter(is_active=True)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(address__icontains=q) | Q(country__icontains=q))

        items = list(qs.values("id", "name", "address", "city", "country", "latitude", "longitude", "store_hours"))

        return JsonResponse({"results": items})
    
    except Exception as e:
        return JsonResponse({"error": "An error occurred while fetching stores"}, status=500)
