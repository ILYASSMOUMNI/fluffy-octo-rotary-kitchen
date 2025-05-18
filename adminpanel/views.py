from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from chefs.models import ChefApplication, ChefBadge
from users.models import User
from recipes.models import Recipe
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from chefs.models import ChefApplication
from users.models import User
from recipes.models import Recipe
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.models import User
from users.models import User
from django.db.models import Count
from .models import Application

User = get_user_model()

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('adminpanel:admin_login')
    return wrapper

@login_required
@admin_only
def applications_list(request):
    applications = User.objects.filter(chef_application_status__in=['pending', 'approved', 'rejected']).order_by('-date_joined')
    return render(request, 'adminpanel/applications.html', {'applications': applications})

def users_list(request):
    users = User.objects.annotate(recipe_count=Count('recipe'))
    return render(request, 'adminpanel/users.html', {'users': users})

def logout_view(request):
    logout(request )
    return redirect('users:login')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('adminpanel:dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'adminpanel/admin_login.html')

@login_required
@admin_only
def dashboard(request):
    # Get statistics
    total_users = User.objects.count()
    total_chefs = User.objects.filter(role='chef').count()
    pending_applications = User.objects.filter(chef_application_status='pending').count()
    total_recipes = Recipe.objects.count()
    
    # Get recent applications
    recent_applications = User.objects.filter(chef_application_status__in=['pending', 'approved', 'rejected']).order_by('-date_joined')[:5]
    
    # Get recent activities
    recent_activities = [
        {
            'title': 'New User Registration',
            'description': 'A new user has registered on the platform',
            'timestamp': '2 hours ago'
        },
        {
            'title': 'Recipe Published',
            'description': 'A new recipe has been published',
            'timestamp': '3 hours ago'
        },
        {
            'title': 'Chef Application',
            'description': 'A new chef application has been submitted',
            'timestamp': '5 hours ago'
        }
    ]
    
    context = {
        'total_users': total_users,
        'total_chefs': total_chefs,
        'pending_applications': pending_applications,
        'total_recipes': total_recipes,
        'recent_applications': recent_applications,
        'recent_activities': recent_activities
    }
    
    return render(request, 'adminpanel/admin_dashboard.html', context)

@login_required
@admin_only
def approve_application(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.role = 'chef'
        user.chef_application_status = 'approved'
        user.save()
        messages.success(request, f"{user.username} has been approved as a Chef!")
        return redirect('adminpanel:applications_list')
    
    return render(request, 'adminpanel/approve_application.html', {'application': user})

@login_required
@admin_only
def reject_application(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.chef_application_status = 'rejected'
        user.save()
        messages.info(request, f"{user.username}'s application was rejected.")
        return redirect('adminpanel:applications_list')
    
    return render(request, 'adminpanel/reject_application.html', {'application': user})

