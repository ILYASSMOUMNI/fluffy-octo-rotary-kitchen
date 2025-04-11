from django.db import models
from django.conf import settings
from django.utils import timezone
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)  # e.g., "200g", "1 cup", etc.

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class Recipe(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    related_name='created_recipes'
    related_name='liked_recipes' 
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,  # If category is deleted, don't delete recipe
        null=True,  # Allow null values
        blank=True  # Allow blank in forms
    )
    indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['category']),
        ]
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
    servings = models.PositiveIntegerField(default=1)
    instructions = models.TextField()
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
        # Update the likes field to be more explicit
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_recipes'
    )
    def __str__(self):
        return self.title

    def has_chef_badge(self):
        """Check if the recipe creator has a 'chef' role."""
        return self.created_by.role == 'chef'

class Comment(models.Model):
    recipe = models.ForeignKey(
        'Recipe', 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"
    def can_edit(self, user):
        """Check if the user can edit this comment"""
        return user.is_authenticated and (user == self.author or user.is_staff)