from django import forms
from .models import Recipe, Category, Ingredient

class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # You can change this if needed
        required=False  # Make it optional to allow new ingredients
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'category', 'ingredients', 'image','servings', ]


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
