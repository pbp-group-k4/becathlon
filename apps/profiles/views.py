from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import ProfileForm

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
    return JsonResponse({"ok": True, "newsletter_opt_in": prof.newsletter_opt_in})
