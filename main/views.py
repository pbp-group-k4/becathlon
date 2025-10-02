from django.shortcuts import render
from .models import Item

# Create your views here.

def home(request):
    """placeholder"""
    items = Item.objects.all()
    return render(request, 'main/home.html', {'items': items})
