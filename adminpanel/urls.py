from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('applications/', views.applications_list, name='applications_list'),
    path('applications/approve/<int:application_id>/', views.approve_application, name='approve_application'),
    path('applications/reject/<int:application_id>/', views.reject_application, name='reject_application'),
    path('users/', views.users_list, name='users_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.admin_login, name='admin_login'),
]
