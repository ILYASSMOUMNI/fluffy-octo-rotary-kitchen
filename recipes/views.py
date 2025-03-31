from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Category, Ingredient
from .forms import RecipeForm, CategoryForm, IngredientForm
from django.contrib.auth.decorators import login_required
import json



@login_required
def recipe_add(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
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
    recipe = get_object_or_404(Recipe, id=id, created_by=request.user)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            
            # Process ingredients from JSON - similar to recipe_add
            ingredients_json = request.POST.get('ingredients_json')
            if ingredients_json:
                # Clear existing ingredients first to avoid duplicates
                recipe.ingredients.clear()
                
                ingredients_data = json.loads(ingredients_json)
                for item in ingredients_data:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=item['name'],
                        defaults={'quantity': item.get('quantity', '')}
                    )
                    recipe.ingredients.add(ingredient)
            
            return redirect('recipe_list')
    else:
        form = RecipeForm(instance=recipe)

    # Pass current ingredients to the template for displaying in the form
    ingredients = recipe.ingredients.all()
    
    return render(request, 'recipes/recipe_edit.html', {
        'form': form, 
        'recipe': recipe,
        'ingredients': ingredients
    })

@login_required
def recipe_delete(request, id):
    # Get the recipe object by its ID and ensure it belongs to the logged-in user
    recipe = get_object_or_404(Recipe, id=id, created_by=request.user)
    
    if request.method == 'POST':
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

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'recipes/category_list.html', {'categories': categories})
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})
