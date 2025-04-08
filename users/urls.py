from django.contrib import admin
from django.urls import path, include
from . import views
from .views import home
from django.contrib.auth import views as auth_views
from .views import liked_recipes_view
urlpatterns = [
    path('', home, name='home'),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('auth/', include('social_django.urls', namespace='social')),
   path('liked-recipes/', views.liked_recipes_view, name='liked_recipes'),
   path('recipe/<int:id>/like/', views.like_recipe, name='like_recipe'),
]