from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.models import Recipe  # Instead of from .models import Recipe
from django.shortcuts import render


class User(AbstractUser):
    ROLE_CHOICES = [
        ('chef', 'Chef'),
        ('amateur', 'Amateur'),
        ('blogueur', 'Blogueur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
# users/views.py
def my_view():
    from .models import Recipe  # ✅ Import inside the function
from django.shortcuts import render

def home(request):
    return render(request, 'users/home.html')  # ✅ Ensure correct path
