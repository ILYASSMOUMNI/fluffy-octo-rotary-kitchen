# ai_module/forms.py
from django import forms

class IngredientListForm(forms.Form):
    ingredients = forms.CharField(
        label="Enter ingredients you have (comma-separated)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., chicken, onion, tomato paste'}),
        required=True
    )

class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Select image",
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

class ChatForm(forms.Form):
     message = forms.CharField(
         label="Your message",
         max_length=500, # Limit message length
         widget=forms.TextInput(attrs={'autocomplete': 'off'}), # Prevent browser autocomplete
         required=True
     )