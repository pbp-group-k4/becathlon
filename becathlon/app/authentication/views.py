from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistrationForm


def login_view(request):
	"""Authenticate a user and redirect to the homepage."""

	if request.user.is_authenticated:
		messages.info(request, 'You are already signed in.')
		return redirect('home')

	form = LoginForm(request, data=request.POST or None)

	if request.method == 'POST' and form.is_valid():
		user = form.get_user()
		login(request, user)
		messages.success(request, f'Welcome back, {user.first_name or user.username}!')
		return redirect('home')

	return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
	"""Create a new user account and sign them in."""

	if request.user.is_authenticated:
		messages.info(request, 'You already have an active session.')
		return redirect('home')

	form = RegistrationForm(request.POST or None)

	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user)
		messages.success(request, 'Account created successfully! Let’s build your next victory.')
		return redirect('home')

	return render(request, 'authentication/register.html', {'form': form})


@login_required
def logout_view(request):
	"""Terminate the user session and redirect to the homepage."""

	logout(request)
	messages.info(request, 'You have been signed out. See you on the next session!')
	return redirect('home')
