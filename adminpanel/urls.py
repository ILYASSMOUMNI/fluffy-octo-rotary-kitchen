from django.urls import path
from . import views


app_name = 'adminpanel'

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('applications/', views.applications_list, name='applications_list'),
    path('applications/approve/<int:user_id>/', views.approve_application, name='approve_application'),
    path('applications/reject/<int:user_id>/', views.reject_application, name='reject_application'),
    path('users/', views.users_list, name='users_list'),
    path('logout/', views.logout_view, name='logout'),
]
