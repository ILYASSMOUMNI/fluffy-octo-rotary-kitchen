from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, EditProfileForm, RecipeForm
from django.contrib import messages
from .models import Recipe

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
            return redirect('dashboard')
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
            # Log or print the form data before saving to debug
            print("Form data before saving:", form.cleaned_data)
            
            form.save()
            messages.success(request, 'Your profile has been updated!')
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
    return render(request, 'users/home.html')

@login_required
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, created_by=request.user)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('home')  # or wherever you want to redirect after editing
    else:
        form = RecipeForm(instance=recipe)
    
    return render(request, 'users/recipe_edit.html', {
        'form': form,
        'recipe': recipe
    })
