from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient
from django.db.models import Q, Count, Case, When, FloatField
import random

def get_personalized_recommendations(user: User, max_recommendations: int = 10) -> list[dict]:
    """
    Provides personalized recipe recommendations for a logged-in user
    """
    # Gather user preferences - use 'likes' instead of 'liked_by_users'
    liked_recipe_ids = list(user.liked_recipes.values_list('id', flat=True))
    disliked_ingredient_ids = list(user.disliked_ingredients.values_list('id', flat=True))
    preferred_cuisines = user.preferred_cuisines or []

    # Base query
    candidate_recipes_qs = Recipe.objects.all()

    # Apply exclusions
    if liked_recipe_ids:
        candidate_recipes_qs = candidate_recipes_qs.exclude(id__in=liked_recipe_ids)
    if disliked_ingredient_ids:
        candidate_recipes_qs = candidate_recipes_qs.exclude(ingredients__id__in=disliked_ingredient_ids)

    # Calculate scores
    score_annotation = {}
    if preferred_cuisines:
        cuisine_boost = Case(
            *[When(cuisine_type__iexact=cuisine, then=1) for cuisine in preferred_cuisines],
            default=0,
            output_field=FloatField()
        )
        score_annotation['cuisine_score'] = cuisine_boost

    # Apply scoring
    if score_annotation:
        total_score_expression = score_annotation.get('cuisine_score', 0.0)
        candidate_recipes_qs = candidate_recipes_qs.annotate(
            recommendation_score=total_score_expression
        ).order_by('-recommendation_score')
    else:
        candidate_recipes_qs = candidate_recipes_qs.order_by('?')

    # Format results
    recommended_recipes = list(candidate_recipes_qs[:max_recommendations])
    results = []
    for recipe in recommended_recipes:
        score = getattr(recipe, 'recommendation_score', 0.0)
        reason = ""
        if preferred_cuisines and recipe.cuisine_type and recipe.cuisine_type.lower() in [c.lower() for c in preferred_cuisines]:
            reason = f"Matches preferred cuisine: {recipe.cuisine_type}"

        results.append({
            "recipe_id": recipe.id,
            "recipe_title": recipe.title,
            "recipe_description": recipe.description,
            "recipe_image": recipe.image.url if recipe.image else None,
            "score": round(score, 2),
            "reason": reason,
        })

    # Fallback to popular recipes if needed - use 'likes' for counting
    needed = max_recommendations - len(results)
    if needed > 0:
        exclude_ids = [r['recipe_id'] for r in results] + liked_recipe_ids
        fallback_recipes = get_popular_recipes(
            max_recommendations=needed,
            exclude_ids=exclude_ids
        )
        results.extend(fallback_recipes)

    return results

def get_popular_recipes(max_recommendations: int = 10, exclude_ids: list = None) -> list[dict]:
    """Fetches popular recipes based on likes"""
    if exclude_ids is None:
        exclude_ids = []

    # Use 'likes' instead of 'liked_by_users' for counting
    popular_qs = Recipe.objects.annotate(
        num_likes=Count('likes')  # Changed from 'liked_by_users' to 'likes'
    ).filter(
        num_likes__gte=2
    ).exclude(
        id__in=exclude_ids
    ).order_by(
        '-num_likes', '-created_at'
    )

    popular_recipes = list(popular_qs[:max_recommendations])

    # Fallback to random recipes if needed
    needed = max_recommendations - len(popular_recipes)
    if needed > 0:
        current_ids = exclude_ids + [r.id for r in popular_recipes]
        random_recipes = list(Recipe.objects.exclude(id__in=current_ids).order_by('?')[:needed])
        popular_recipes.extend(random_recipes)

    # Format results
    results = []
    for recipe in popular_recipes:
        num_likes = getattr(recipe, 'num_likes', 0)
        reason = f"Popular ({num_likes} likes)" if num_likes > 0 else "New or less known"
        results.append({
            "recipe_id": recipe.id,
            "recipe_title": recipe.title,
            "recipe_description": recipe.description,
            "recipe_image": recipe.image.url if recipe.image else None,
            "score": num_likes,
            "reason": reason,
        })

    return results