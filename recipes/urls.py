from django.urls import path
from . import views
from .views import recipe_search, edit_comment
app_name = 'recipes'
urlpatterns = [
    path('add/', views.recipe_add, name='recipe_add'),
    path('list/', views.recipe_list, name='recipe_list'),
    path('<int:id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<int:id>/delete/', views.recipe_delete, name='recipe_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:id>/', views.recipe_by_category, name='recipe_by_category'),
    path('<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('search/', recipe_search, name='recipe_search'),
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('pending/', views.pending_recipes, name='pending_recipes'),
    path('approve/<int:recipe_id>/', views.approve_recipe, name='approve_recipe'),
    path('reject/<int:recipe_id>/', views.reject_recipe, name='reject_recipe'),
    path('my-status/', views.my_recipe_status, name='my_recipe_status'),
    
]
