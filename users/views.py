from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, EditProfileForm
from django.contrib import messages
from recipes.models import Recipe
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()

# Register View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('users:home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'users/login.html')

# Dashboard View (only accessible when logged in)
@login_required
def dashboard_view(request):
    # Pass the user's role (chef, amateur, blogueur) to the template
    return render(request, 'users/dashboard.html', {'user': request.user})

# Edit Profile View (only accessible when logged in)
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')  # Redirect to dashboard after success
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Home View (public access)
def home(request):
    recipes = Recipe.objects.all()[:6]  # Get latest 6 recipes
    return render(request, 'users/home.html', {'recipes': recipes})
 
@login_required
def liked_recipes_view(request):
    # Use 'liked_recipes' which is the related_name from User model
    liked_recipes = request.user.liked_recipes.all().order_by('-created_at')
    paginator = Paginator(liked_recipes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/liked_recipes.html', {
        'page_obj': page_obj,
        'liked_recipes': liked_recipes
    })
@login_required
def like_recipe(request, id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=id)
        if request.user in recipe.likes.all():
            recipe.likes.remove(request.user)
            liked = False
        else:
            recipe.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'like_count': recipe.likes.count()
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def request_chef_status(request):
    if request.method == 'POST':
        user = request.user
        if user.chef_application_status == 'not_applied':
            user.chef_application_status = 'pending'
            user.save()
            messages.success(request, 'Your chef application has been submitted for review.')
        else:
            messages.warning(request, 'You have already submitted an application.')
        return redirect('users:profile')
    return render(request, 'users/request_chef.html')

@login_required
def process_chef_application(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    try:
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'approve':
                user.role = 'chef'
                user.chef_application_status = 'approved'
                user.save()
                messages.success(request, f'{user.username} has been approved as a chef.')
            elif action == 'reject':
                user.chef_application_status = 'rejected'
                user.save()
                messages.warning(request, f'{user.username}\'s application has been rejected.')
            return redirect('adminpanel:dashboard')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('adminpanel:dashboard')
    
    return render(request, 'users/process_application.html', {'applicant': user})