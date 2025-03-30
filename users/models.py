# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
# Remove: from django.shortcuts import render # Belongs in views

# Import Recipe using its app path if needed for relationships
# Note: Using strings avoids potential circular imports during initialization
# 'recipes.Recipe', 'recipes.Ingredient'

class User(AbstractUser):
    ROLE_CHOICES = [
        ('chef', 'Chef'),
        ('amateur', 'Amateur'),
        ('blogueur', 'Blogueur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True) # Allow blank role?
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # --- Add Preference Fields Here ---
    # Use strings 'app_name.ModelName' for M2M fields to avoid import issues
    liked_recipes = models.ManyToManyField(
        'recipes.Recipe',
        blank=True,
        related_name='liked_by_users' # Important for the recommender query
    )
    disliked_ingredients = models.ManyToManyField(
        'recipes.Ingredient',
        blank=True,
        related_name='disliked_by_users' # Important for the recommender query
    )
    preferred_cuisines = models.JSONField(
        default=list,
        blank=True,
        null=True # Allow null if blank=True
    )

    def __str__(self):
        # Avoid error if role is blank:
        role_display = self.get_role_display() if self.role else "No Role"
        return f"{self.username} ({role_display})"