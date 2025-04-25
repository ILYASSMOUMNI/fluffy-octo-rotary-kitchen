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

User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('psswd')
admin.save()

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'adminpanel/admin_login.html')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('adminpanel:admin_login')
    
    # Get statistics
    total_users = User.objects.count()
    total_chefs = User.objects.filter(role='chef').count()
    pending_applications = ChefApplication.objects.filter(status='pending').count()
    total_recipes = Recipe.objects.count()
    
    # Get recent applications
    recent_applications = ChefApplication.objects.order_by('-created_at')[:5]
    
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

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('adminpanel:admin_login')
    return wrapper

@login_required
def dashboard(request):
    # If user is admin, redirect to admin dashboard
    if request.user.role == 'admin':
        return redirect('adminpanel:admin_dashboard')
    
    # Regular dashboard for non-admin users
    chef_applications = ChefApplication.objects.all().order_by('-created_at')
    chefs = User.objects.filter(role='chef')
    context = {
        'chef_applications': chef_applications,
        'chefs': chefs,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
@admin_only
def admin_dashboard(request):
    # Get statistics
    total_users = User.objects.count()
    total_chefs = User.objects.filter(role='chef').count()
    pending_applications = ChefApplication.objects.filter(status='pending').count()
    total_recipes = Recipe.objects.count()
    
    # Get recent applications
    recent_applications = ChefApplication.objects.order_by('-created_at')[:5]
    
    # Get recent activities (you can customize this based on your needs)
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
    
    return render(request, 'adminpanel/dashboard.html', context)



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

