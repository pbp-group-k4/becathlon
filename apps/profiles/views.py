from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from .forms import ProfileForm
from apps.main.models import Product

@login_required
def detail(request):
    return render(request, "profiles/profile_detail.html", {"profile": request.user.profile})

@login_required
def edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect("profiles:detail")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/profile_edit.html", {"form": form})

# ---- Optional: tiny AJAX endpoint to toggle newsletter flag
@login_required
def toggle_newsletter_ajax(request):
    if request.method != "POST" or request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return HttpResponseBadRequest("Invalid request")
    prof = request.user.profile
    prof.newsletter_opt_in = not prof.newsletter_opt_in
    prof.save(update_fields=["newsletter_opt_in"])
    return JsonResponse({
        "success": True,
        "data": {"newsletter_opt_in": prof.newsletter_opt_in},
        "error": None
    })


@login_required
@require_POST
def switch_account_type_ajax(request):
    """Switch account type between BUYER and SELLER with warning about delisting products"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest("Invalid request")
    
    profile = request.user.profile
    new_account_type = request.POST.get('account_type', '').upper()
    
    # Validate account type
    if new_account_type not in ['BUYER', 'SELLER']:
        return JsonResponse({'success': False, 'error': 'Invalid account type'}, status=400)
    
    # If switching TO BUYER, delist all products
    if new_account_type == 'BUYER' and profile.account_type == 'SELLER':
        # Delete all products created by this user
        Product.objects.filter(created_by=request.user).delete()
        profile.account_type = 'BUYER'
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Account type switched to Buyer. All your listed products have been removed.',
            'account_type': profile.account_type
        })
    
    # If switching TO SELLER, just update
    if new_account_type == 'SELLER' and profile.account_type == 'BUYER':
        profile.account_type = 'SELLER'
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Account type switched to Seller. You can now list products.',
            'account_type': profile.account_type
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Account type already set'
    }, status=400)
