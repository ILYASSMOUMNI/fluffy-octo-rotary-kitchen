from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Category, Ingredient
from .forms import RecipeForm, CategoryForm, IngredientForm, EditCommentForm
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Q
from .forms import CommentForm
from .models import Comment
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages

@login_required
def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            
            # Auto-approve if created by a chef
            if request.user.role == 'chef':
                recipe.approval_status = 'approved'
                recipe.approved_by = request.user
                recipe.approval_date = timezone.now()
            else:
                # Set to pending for non-chefs
                recipe.approval_status = 'pending'
            
            recipe.save()
            
            # Process ingredients from JSON
            ingredients_json = request.POST.get('ingredients_json')
            if ingredients_json:
                ingredients_data = json.loads(ingredients_json)
                for item in ingredients_data:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=item['name'],
                        defaults={'quantity': item.get('quantity', '')}
                    )
                    recipe.ingredients.add(ingredient)
            
            # Show success message with appropriate text based on approval status
            if request.user.role == 'chef':
                messages.success(request, 'Recipe created and automatically approved!')
            else:
                messages.success(request, 'Recipe created! It will be reviewed by our chefs before being published.')
            
            return redirect('recipe_list')
    else:
        form = RecipeForm()

    categories = Category.objects.all()
    return render(request, 'recipes/add_recipe.html', {
        'form': form,
        'categories': categories,
        'has_categories': categories.exists()
    })
@login_required
def recipe_edit(request, id):
    # Get the recipe object by its ID
    recipe = get_object_or_404(Recipe, id=id)
    
    # Check if user is the creator or a chef
    if request.user != recipe.created_by and request.user.role != 'chef':
        return HttpResponseForbidden("You don't have permission to edit this recipe")
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            
            # Process ingredients from JSON
            ingredients_json = request.POST.get('ingredients_json')
            if ingredients_json:
                # Clear existing ingredients first to avoid duplicates
                recipe.ingredients.clear()
                
                ingredients_data = json.loads(ingredients_json)
                for item in ingredients_data:
                    # Get or create the ingredient, but handle potential duplicates
                    try:
                        ingredient = Ingredient.objects.get(
                            name=item['name'],
                            quantity=item.get('quantity', '')
                        )
                    except Ingredient.DoesNotExist:
                        # If it doesn't exist, create it
                        ingredient = Ingredient.objects.create(
                            name=item['name'],
                            quantity=item.get('quantity', '')
                        )
                    except Ingredient.MultipleObjectsReturned:
                        # If there are duplicates, get the first one
                        ingredient = Ingredient.objects.filter(
                            name=item['name'],
                            quantity=item.get('quantity', '')
                        ).first()
                    
                    recipe.ingredients.add(ingredient)
            
            # Process instructions from JSON
            instructions_json = request.POST.get('instructions_json')
            if instructions_json:
                instructions_data = json.loads(instructions_json)
                instructions_text = "\n".join([step['text'] for step in instructions_data if 'text' in step])
                recipe.instructions = instructions_text
            
            recipe.save()
            return redirect('recipe_list')
    else:
        form = RecipeForm(instance=recipe)

    # Get current ingredients and format them as JSON
    ingredients = recipe.ingredients.all().distinct()  # Add distinct() to avoid duplicates
    ingredients_json = json.dumps([
        {'name': ing.name, 'quantity': ing.quantity} 
        for ing in ingredients
    ])
    
    instructions_text = recipe.instructions or ""
    instructions_data = [{'text': step.strip()} for step in instructions_text.split('\n') if step.strip()]
    instructions_json = json.dumps(instructions_data)
    
    return render(request, 'recipes/recipe_edit.html', {
        'form': form, 
        'recipe': recipe,
        'ingredients': ingredients,
        'ingredients_json': ingredients_json,
        'instructions_json': instructions_json
    })
@login_required
def recipe_delete(request, id):
    # Get the recipe object by its ID
    recipe = get_object_or_404(Recipe, id=id)
    
    # Check if user is the creator or a chef
    if request.user != recipe.created_by and request.user.role != 'chef':
        return HttpResponseForbidden("You don't have permission to delete this recipe")
    
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')  # Redirect to the recipe list after deleting
    
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})

@login_required
def recipe_list(request):
    """Modified recipe list to only show approved recipes to non-chefs"""
    if request.user.role == 'chef':
        recipes = Recipe.objects.all()
    else:
        recipes = Recipe.objects.filter(approval_status='approved')
    
    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes
    })

def recipe_by_category(request, id):
    category = get_object_or_404(Category, id=id)  # Get the category by its ID
    recipes = Recipe.objects.filter(category=category)  # Filter recipes by the category
    
    return render(request, 'recipes/recipe_by_category.html', {
        'category': category,
        'recipes': recipes
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'recipes/category_list.html', {'categories': categories})
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    
    # Handle like/unlike action
    if request.method == 'POST' and 'like' in request.POST:
        if request.user.is_authenticated:
            if request.user in recipe.likes.all():
                recipe.likes.remove(request.user)
            else:
                recipe.likes.add(request.user)
            return redirect('recipe_detail', id=id)
    
    # Check if current user has liked this recipe
    is_liked = request.user.is_authenticated and request.user in recipe.likes.all()
    
    # Handle comment submission
    if request.method == 'POST' and 'comment' in request.POST and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', id=id)
    else:
        comment_form = CommentForm()
    
    # Get all comments for this recipe
    comments = Comment.objects.filter(recipe=recipe).order_by('-created_at')
    
    context = {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'like_count': recipe.likes.count()
    }
    return render(request, 'recipes/recipe_detail.html', context)
def recipe_search(request):
    query = request.GET.get('q', '').strip()
    results = Recipe.objects.all()
    
    if query:
        # Initialize the search query
        search_query = Q(title__icontains=query) | Q(description__icontains=query)
        
        # Only add category search if the query might match category names
        if len(query) >= 2:  # Only search categories for queries of 2+ characters
            search_query |= Q(category__name__icontains=query)
        
        # Add ingredient search
        search_query |= Q(ingredients__name__icontains=query)
        
        results = results.filter(search_query).distinct()
    
    context = {
        'recipes': results,
        'query': query
    }
    return render(request, 'recipes/search_results.html', context)
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if not comment.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to edit this comment")
    
    if request.method == 'POST':
        form = EditCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', id=comment.recipe.id)
    else:
        form = EditCommentForm(instance=comment)
    
    return render(request, 'recipes/edit_comment.html', {
        'form': form,
        'comment': comment
    })

@login_required
def pending_recipes(request):
    """View for chefs to see and manage pending recipes"""
    if request.user.role != 'chef':
        return HttpResponseForbidden("Only chefs can access this page")
    
    pending_recipes = Recipe.objects.filter(approval_status='pending')
    return render(request, 'recipes/pending_recipes.html', {
        'pending_recipes': pending_recipes
    })

@login_required
def approve_recipe(request, recipe_id):
    """View for chefs to approve a recipe"""
    if request.user.role != 'chef':
        return HttpResponseForbidden("Only chefs can approve recipes")
    
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.approval_status != 'pending':
        return HttpResponseForbidden("This recipe is not pending approval")
    
    recipe.approve(request.user)
    return redirect('pending_recipes')

@login_required
def reject_recipe(request, recipe_id):
    """View for chefs to reject a recipe"""
    if request.user.role != 'chef':
        return HttpResponseForbidden("Only chefs can reject recipes")
    
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.approval_status != 'pending':
        return HttpResponseForbidden("This recipe is not pending approval")
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        recipe.reject(request.user, reason)
        return redirect('pending_recipes')
    
    return render(request, 'recipes/reject_recipe.html', {
        'recipe': recipe
    })

@login_required
def my_recipe_status(request):
    """View for users to see their recipe status"""
    # Get all recipes created by the user
    user_recipes = Recipe.objects.filter(created_by=request.user)
    
    # Count recipes by status
    approved_count = user_recipes.filter(approval_status='approved').count()
    pending_count = user_recipes.filter(approval_status='pending').count()
    rejected_count = user_recipes.filter(approval_status='rejected').count()
    
    # If user is a chef, show all their recipes
    if request.user.role == 'chef':
        return render(request, 'recipes/my_recipe_status.html', {
            'user_recipes': user_recipes,
            'approved_count': approved_count,
            'pending_count': pending_count,
            'rejected_count': rejected_count,
            'is_chef': True
        })
    # For amateur and blogueur users
    elif request.user.role in ['amateur', 'blogueur']:
        return render(request, 'recipes/my_recipe_status.html', {
            'user_recipes': user_recipes,
            'approved_count': approved_count,
            'pending_count': pending_count,
            'rejected_count': rejected_count,
            'is_chef': False
        })
    else:
        return HttpResponseForbidden("This page is only for chefs, amateur, and blogueur users")