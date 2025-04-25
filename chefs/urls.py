from django.urls import path
from . import views

app_name = 'chefs'

urlpatterns = [
    path('apply/', views.apply_chef, name='apply_chef'),
    path('applications/', views.manage_applications, name='manage_applications'),
    path('applications/<int:application_id>/process/', views.process_application, name='process_application'),
    path('chef/<int:user_id>/award-badge/', views.award_badge, name='award_badge'),
] 