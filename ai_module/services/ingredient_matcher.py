# ai_module/services/ingredient_matcher.py
from recipes.models import Recipe, Ingredient

def suggest_recipes_by_ingredients(available_ingredient_names: list[str], max_suggestions: int = 5) -> list[dict]:
    """Suggests recipes based on available ingredients using Django ORM."""
    available_set = set(name.lower().strip() for name in available_ingredient_names)
    
    # Fetch potentially relevant ingredients from DB (optimization possible)
    # This is simple but might be slow for large DBs. Consider pre-filtering.
    all_recipes = Recipe.objects.prefetch_related('ingredients').all() 
    
    suggestions = []

    for recipe in all_recipes:
        required_ingredients = recipe.ingredients.all() # Get related Ingredient objects
        required_set = set(ing.name.lower().strip() for ing in required_ingredients)

        if not required_set:
            continue

        matched_ingredients_objs = [ing for ing in required_ingredients if ing.name.lower() in available_set]
        matched_ingredients_names = set(ing.name.lower() for ing in matched_ingredients_objs)
        
        missing_ingredients_names = required_set.difference(matched_ingredients_names)

        if len(matched_ingredients_names) > 0:
            match_score = len(matched_ingredients_names) / len(required_set)
            score = match_score * (1 / (1 + len(missing_ingredients_names)))

            suggestions.append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "score": score,
                "matched_count": len(matched_ingredients_names),
                "missing_count": len(missing_ingredients_names),
                "missing_ingredients": list(missing_ingredients_names),
            })

    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions[:max_suggestions]

# --- Adapt recommender.py similarly, fetching UserProfile ---
# from users.models import UserProfile
# def get_personalized_recommendations(user: User, max_recommendations: int = 5) -> list[dict]:
#    try:
#        profile = user.profile # Access UserProfile via related_name
#        # Use profile.liked_recipes, profile.disliked_ingredients, etc.
#        # Query Recipe model based on preferences...
#    except UserProfile.DoesNotExist:
#        # Handle case where user has no profile
#        return [] # Or return popular recipes
#    # ... rest of logic ...


# --- Adapt image_recognizer.py ---
# Needs secure handling of API keys from settings.py
# from django.conf import settings
# GOOGLE_VISION_API_KEY = settings.GOOGLE_VISION_API_KEY
# (Rest of the function is similar, taking image_path as input)

# --- Adapt chatbot.py ---
# Will likely call other service functions like suggest_recipes_by_ingredients
# Needs state management (Django sessions, database, or external store)