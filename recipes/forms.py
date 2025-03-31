from django import forms
from .models import Recipe, Category, Ingredient
import json

class RecipeForm(forms.ModelForm):
    ingredients_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    instructions_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'category', 'servings', 'image', 'ingredients_json', 'instructions_json']
        
    def clean(self):
        cleaned_data = super().clean()
        ingredients_json = cleaned_data.get('ingredients_json')
        instructions_json = cleaned_data.get('instructions_json')
        
        if not ingredients_json:
            self.add_error('ingredients_json', 'Ingredients are required.')
        if not instructions_json:
            self.add_error('instructions_json', 'Instructions are required.')
            
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Process ingredients
        ingredients_json = self.cleaned_data.get('ingredients_json')
        if ingredients_json and commit:
            # Clear existing ingredients to avoid duplicates
            instance.ingredients.clear()
            
            ingredients_data = json.loads(ingredients_json)
            for item in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    defaults={'quantity': item.get('quantity', '')}
                )
                instance.ingredients.add(ingredient)
        
        # Process instructions
        instructions_json = self.cleaned_data.get('instructions_json')
        if instructions_json:
            instructions_data = json.loads(instructions_json)
            instance.instructions = "\n".join(
                [f"{idx+1}. {item['text']}" for idx, item in enumerate(instructions_data)]
            )
        
        if commit:
            instance.save()
            
        return instance

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