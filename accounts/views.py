from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validations
        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required!')
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken! Try another one.')
            return render(request, 'accounts/signup.html', {'email': email})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered! Try logging in.')
            return render(request, 'accounts/signup.html', {'username': username})

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, f'Welcome to KTM Bus Finder, {user.username}!')
        return redirect('home')

    return render(request, 'accounts/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'accounts/login.html', {'username': username})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def profile_view(request):
    from bus.models import FavoriteRoute
    favorites = FavoriteRoute.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'favorites': favorites})