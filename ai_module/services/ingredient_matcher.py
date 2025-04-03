from django.db.models import Count, Q
from recipes.models import Recipe, Ingredient

def suggest_recipes_by_ingredients(user_ingredients: list[str], min_matches=1) -> list[dict]:
    """
    Find recipes that match the provided ingredients
    Returns simplified results without scores
    """
    # Normalize user ingredients
    user_ingredients = [ing.strip().lower() for ing in user_ingredients if ing.strip()]
    if not user_ingredients:
        return []

    # Build matching conditions
    conditions = Q()
    for ing in user_ingredients:
        conditions |= Q(ingredients__name__icontains=ing)
        if ing.endswith('s'):
            conditions |= Q(ingredients__name__icontains=ing[:-1])  # Try singular
        else:
            conditions |= Q(ingredients__name__icontains=ing + 's')  # Try plural

    # Find matching recipes
    recipes = (
        Recipe.objects
        .prefetch_related('ingredients')
        .filter(conditions)
        .annotate(
            match_count=Count('ingredients', filter=conditions),
            total_ingredients=Count('ingredients')
        )
        .filter(match_count__gte=min_matches)
        .distinct()
    )

    # Prepare simplified results
    results = []
    for recipe in recipes:
        recipe_ings = {ing.name.lower(): ing for ing in recipe.ingredients.all()}
        
        matched = []
        missing = []
        
        for ing_name, ing_obj in recipe_ings.items():
            if any(user_ing in ing_name or ing_name.startswith(user_ing) 
               for user_ing in user_ingredients):
                matched.append(f"{ing_obj.name} ({ing_obj.quantity})")
            else:
                missing.append(f"{ing_obj.name} ({ing_obj.quantity})")

        results.append({
            'recipe_id': recipe.id,
            'recipe_name': recipe.title,
            'matched_count': len(matched),
            'missing_count': len(missing),
            'missing_ingredients': missing,
            'image_url': recipe.image.url if recipe.image else None,
        })

    # Sort by most matched ingredients first, then fewest missing
    return sorted(results, key=lambda x: (-x['matched_count'], x['missing_count']))