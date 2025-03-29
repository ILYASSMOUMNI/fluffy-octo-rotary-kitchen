from django.db import models

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
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')
    servings = models.IntegerField(null=True, blank=True)
    instructions = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
