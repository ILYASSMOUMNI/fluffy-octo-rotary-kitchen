from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category, Ingredient

class Command(BaseCommand):
    help = 'Creates sample recipes for testing'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Get or create categories
        categories = {
            'Breakfast': ['Pancakes', 'Omelette', 'French Toast'],
            'Lunch': ['Caesar Salad', 'Club Sandwich', 'Pasta Salad'],
            'Dinner': ['Spaghetti Bolognese', 'Grilled Chicken', 'Beef Stir Fry'],
            'Dessert': ['Chocolate Cake', 'Apple Pie', 'Ice Cream'],
            'Snack': ['Popcorn', 'Trail Mix', 'Fruit Smoothie']
        }

        # Create categories and recipes
        for category_name, recipe_names in categories.items():
            category, _ = Category.objects.get_or_create(name=category_name)
            
            for recipe_name in recipe_names:
                recipe, created = Recipe.objects.get_or_create(
                    title=recipe_name,
                    defaults={
                        'created_by': user,
                        'description': f'Delicious {recipe_name} recipe',
                        'category': category,
                        'servings': 4,
                        'instructions': f'Instructions for making {recipe_name}'
                    }
                )
                
                if created:
                    # Add some ingredients
                    ingredients = [
                        Ingredient.objects.create(name=f'Ingredient 1 for {recipe_name}', quantity='2 cups'),
                        Ingredient.objects.create(name=f'Ingredient 2 for {recipe_name}', quantity='1 tbsp'),
                        Ingredient.objects.create(name=f'Ingredient 3 for {recipe_name}', quantity='3 pieces')
                    ]
                    recipe.ingredients.add(*ingredients)
                    self.stdout.write(self.style.SUCCESS(f'Created recipe: {recipe_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample recipes')) 