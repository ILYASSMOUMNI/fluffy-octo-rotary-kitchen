from django import forms
from .models import Recipe, Category, Ingredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'category', 'ingredients', 'servings', 'instructions', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
        }
        ingredients = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter ingredients (comma-separated)', 'rows': 4}),
        required=False
        )
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']
   
def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        if ingredients:
            # Ensure ingredients are split by commas and strip extra spaces
            return [ingredient.strip() for ingredient in ingredients.split(',')]
        return []
