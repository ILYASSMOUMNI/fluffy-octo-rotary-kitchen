from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChefApplication, ChefBadge
from django.conf import settings
from django.utils import timezone

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.email == settings.ADMIN_EMAIL:
            return view_func(request, *args, **kwargs)
        return redirect('users:login')
    return wrapper

@login_required
def apply_chef(request):
    if request.method == 'POST':
        # Check if user already has a pending application
        existing_application = ChefApplication.objects.filter(
            user=request.user,
            status='pending'
        ).exists()
        
        if existing_application:
            messages.warning(request, 'You already have a pending application.')
            return redirect('profile')
        
        application = ChefApplication.objects.create(
            user=request.user,
            motivation=request.POST.get('motivation'),
            experience=request.POST.get('experience')
        )
        messages.success(request, 'Your application has been submitted successfully!')
        return redirect('profile')
    
    return render(request, 'chefs/apply_chef.html')

@login_required
@admin_only
def manage_applications(request):
    applications = ChefApplication.objects.all().order_by('-created_at')
    return render(request, 'chefs/manage_applications.html', {'applications': applications})

@login_required
@admin_only
def process_application(request, application_id):
    application = get_object_or_404(ChefApplication, id=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            application.status = 'approved'
            application.user.role = 'chef'
            application.user.save()
            messages.success(request, f'Application approved. {application.user.username} is now a chef!')
        elif action == 'reject':
            application.status = 'rejected'
            application.rejection_reason = request.POST.get('rejection_reason', '')
            messages.warning(request, 'Application rejected.')
        
        application.processed_at = timezone.now()
        application.processed_by = request.user
        application.save()
        
        return redirect('manage_applications')
    
    return render(request, 'chefs/process_application.html', {'application': application})

@login_required
@admin_only
def award_badge(request, user_id):
    if request.method == 'POST':
        chef = get_object_or_404(settings.AUTH_USER_MODEL, id=user_id)
        badge = ChefBadge.objects.create(
            chef=chef,
            badge_type=request.POST.get('badge_type'),
            description=request.POST.get('description', ''),
            awarded_by=request.user
        )
        messages.success(request, f'Badge awarded to {chef.username}!')
        return redirect('chef_profile', user_id=user_id)
    
    return render(request, 'chefs/award_badge.html')
