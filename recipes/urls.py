from django.urls import path
from . import views

urlpatterns = [
       path('add/', views.recipe_add, name='recipe_add'),
    path('list/', views.recipe_list, name='recipe_list'),
    path('<int:id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<int:id>/delete/', views.recipe_delete, name='recipe_delete'),
]
