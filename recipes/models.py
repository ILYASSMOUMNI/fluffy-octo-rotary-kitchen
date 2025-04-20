from django.db import models
from django.conf import settings
from django.utils import timezone
from cloudinary.models import CloudinaryField

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
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
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
    image = CloudinaryField('image', folder='recipe_images', null=True, blank=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_recipes'
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_recipes'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def needs_approval(self):
        """Check if the recipe needs approval based on the creator's role"""
        return self.created_by.role not in ['chef']

    def approve(self, approved_by):
        """Approve the recipe"""
        if approved_by.role != 'chef':
            raise ValueError("Only chefs can approve recipes")
        self.approval_status = 'approved'
        self.approved_by = approved_by
        self.approval_date = timezone.now()
        self.save()

    def reject(self, rejected_by, reason):
        """Reject the recipe"""
        if rejected_by.role != 'chef':
            raise ValueError("Only chefs can reject recipes")
        self.approval_status = 'rejected'
        self.approved_by = rejected_by
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save()

    def is_approved(self):
        """Check if the recipe is approved"""
        return self.approval_status == 'approved'

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