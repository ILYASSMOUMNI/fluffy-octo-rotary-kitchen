from django import forms
from .models import Recipe, Category, Ingredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'category', 'ingredients', 'servings', 'instructions', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control'}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'})
        }
   
def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        if ingredients:
            # Ensure ingredients are split by commas and strip extra spaces
            return [ingredient.strip() for ingredient in ingredients.split(',')]
        return []
