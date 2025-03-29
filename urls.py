from django.urls import path
from . import views

urlpatterns = [
    # ... your other URL patterns ...
    path('recipe/edit/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
] 