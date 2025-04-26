# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from recipes.models import Recipe
# Remove: from django.shortcuts import render # Belongs in views

# Import Recipe using its app path if needed for relationships
# Note: Using strings avoids potential circular imports during initialization
# 'recipes.Recipe', 'recipes.Ingredient'

class User(AbstractUser):
    ROLE_CHOICES = [
        ('blogueur', 'Blogueur'),
        ('chef', 'Chef'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='blogueur')
    bio = models.TextField(blank=True, null=True)
    profile_picture = CloudinaryField('image', folder='profile_pictures', blank=True, null=True)
    chef_application_status = models.CharField(
        max_length=20,
        choices=[
            ('not_applied', 'Not Applied'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='not_applied'
    )

    # --- Add Preference Fields Here ---
    # Use strings 'app_name.ModelName' for M2M fields to avoid import issues
    saved_recipes = models.ManyToManyField(
        'recipes.Recipe',
        blank=True,
        related_name='saved_by_users'
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
    def has_liked(self, recipe):
        return self.liked_recipes.filter(pk=recipe.pk).exists()
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'chef'  # Superusers are automatically chefs
            self.chef_application_status = 'approved'
        super().save(*args, **kwargs)