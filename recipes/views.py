from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Category, Ingredient
from .forms import RecipeForm, CategoryForm, IngredientForm
from django.contrib.auth.decorators import login_required

@login_required
def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            # Assign the recipe to the logged-in user
            recipe = form.save(commit=False)
            recipe.created_by = request.user  # Changed from user to created_by
            recipe.save()

            # For ManyToManyField, we need to save the form first
            form.save_m2m()  # This saves the ingredients relationship
            
            return redirect('recipe_list')
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = RecipeForm()
    
    # Add context to help diagnose issues
    categories = Category.objects.all()
    return render(request, 'recipes/add_recipe.html', {
        'form': form,
        'categories': categories,
        'has_categories': categories.exists()
    })
def recipe_edit(request, id):
    # Get the recipe object by its ID
    recipe = get_object_or_404(Recipe, id=id, user=request.user)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_list')  # Redirect to the recipe list after saving
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/recipe_edit.html', {'form': form, 'recipe': recipe})

@login_required
def recipe_delete(request, id):
    # Get the recipe object by its ID and ensure it belongs to the logged-in user
    recipe = get_object_or_404(Recipe, id=id, user=request.user)
    
    if request.method == 'POST':
        # Delete the recipe
        recipe.delete()
        return redirect('recipe_list')  # Redirect to the recipe list after deleting
    
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})

@login_required
def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})
def recipe_by_category(request, id):
    category = get_object_or_404(Category, id=id)  # Get the category by its ID
    recipes = Recipe.objects.filter(category=category)  # Filter recipes by the category
    
    return render(request, 'recipes/recipe_by_category.html', {
        'category': category,
        'recipes': recipes
    })
