# ai_module/services/recommender.py

# Use Django's recommended way to get the User model
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient # Assuming your models are in the 'recipes' app
# Remove: from users.models import UserProfile <<< No longer needed
from django.db.models import Q, Count, Case, When, FloatField
# Remove: from django.core.exceptions import ObjectDoesNotExist <<< Not needed for profile check now
import random

# --- Configuration ---
DEFAULT_MAX_RECOMMENDATIONS = 10
POPULARITY_THRESHOLD = 2

User = get_user_model() # Get the active User model (your custom one)

def get_personalized_recommendations(user: User, max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS) -> list[dict]:
    """
    Provides personalized recipe recommendations for a logged-in user
    using the custom User model.
    """
    # No need to check for profile anymore, we operate directly on the user object

    # --- Gather User Preferences (Directly from User object) ---
    liked_recipe_ids = list(user.liked_recipes.values_list('id', flat=True))
    disliked_ingredient_ids = list(user.disliked_ingredients.values_list('id', flat=True))
    preferred_cuisines = user.preferred_cuisines or [] # Ensure it's a list

    # --- Base Query: Start with all recipes ---
    candidate_recipes_qs = Recipe.objects.all()

    # --- Apply Exclusions ---
    # 1. Exclude already liked recipes
    if liked_recipe_ids:
        candidate_recipes_qs = candidate_recipes_qs.exclude(id__in=liked_recipe_ids)

    # 2. Exclude recipes containing disliked ingredients
    if disliked_ingredient_ids:
        candidate_recipes_qs = candidate_recipes_qs.exclude(ingredients__id__in=disliked_ingredient_ids)

    # --- Calculate Scores ---
    score_annotation = {}

    # 3. Boost score for matching preferred cuisines
    if preferred_cuisines:
        cuisine_boost = Case(
            *[When(cuisine_type__iexact=cuisine, then=1) for cuisine in preferred_cuisines],
            default=0,
            output_field=FloatField()
        )
        score_annotation['cuisine_score'] = cuisine_boost

    # --- Apply Scoring Annotations ---
    if score_annotation:
        total_score_expression = score_annotation.get('cuisine_score', 0.0)
        candidate_recipes_qs = candidate_recipes_qs.annotate(
            recommendation_score=total_score_expression
        )
        candidate_recipes_qs = candidate_recipes_qs.order_by('-recommendation_score')
    else:
        candidate_recipes_qs = candidate_recipes_qs.order_by('?')

    # --- Fetch and Format Results ---
    recommended_recipes = list(candidate_recipes_qs[:max_recommendations])

    results = []
    for recipe in recommended_recipes:
        score = getattr(recipe, 'recommendation_score', 0.0)
        reason = ""
        if preferred_cuisines and recipe.cuisine_type and recipe.cuisine_type.lower() in [c.lower() for c in preferred_cuisines]:
             reason = f"Matches preferred cuisine: {recipe.cuisine_type}"

        results.append({
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "score": round(score, 2),
            "reason": reason,
        })

    # --- Fallback Logic ---
    needed = max_recommendations - len(results)
    if needed > 0:
        print(f"Found {len(results)} personalized recommendations. Fetching {needed} popular fallback(s).")
        exclude_ids = [r['recipe_id'] for r in results] + liked_recipe_ids
        fallback_recipes = get_popular_recipes(
            max_recommendations=needed,
            exclude_ids=exclude_ids
        )
        for recipe_data in fallback_recipes:
             recipe_data['reason'] = recipe_data.get('reason', "Popular recipe")
             results.append(recipe_data)

    return results


def get_popular_recipes(max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS, exclude_ids: list = None) -> list[dict]:
    """
    Fetches popular recipes based on the number of users who liked them.
    (This function likely doesn't need changes if the related_name='liked_by_users'
     was set correctly on the User model's liked_recipes field)
    """
    if exclude_ids is None:
        exclude_ids = []

    # Assuming related_name='liked_by_users' on User.liked_recipes
    popular_qs = Recipe.objects.annotate(
        num_likes=Count('liked_by_users')
    ).filter(
        num_likes__gte=POPULARITY_THRESHOLD
    ).exclude(
        id__in=exclude_ids
    ).order_by(
        '-num_likes', '-created_at'
    )

    popular_recipes = list(popular_qs[:max_recommendations])

    needed = max_recommendations - len(popular_recipes)
    if needed > 0:
        current_ids = exclude_ids + [r.id for r in popular_recipes]
        random_recipes = list(Recipe.objects.exclude(id__in=current_ids).order_by('?')[:needed])
        popular_recipes.extend(random_recipes)

    results = []
    for recipe in popular_recipes:
        num_likes = getattr(recipe, 'num_likes', 0)
        reason = f"Popular ({num_likes} likes)" if num_likes > 0 else "New or less known"
        results.append({
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "score": num_likes,
            "reason": reason,
        })

    return results