from django.core.management.base import BaseCommand
from recipes.models import Category

class Command(BaseCommand):
    help = 'Creates basic recipe categories'

    def handle(self, *args, **kwargs):
        categories = [
            'Breakfast',
            'Lunch',
            'Dinner',
            'Dessert',
            'Snack',
            'Appetizer',
            'Soup',
            'Salad',
            'Main Course',
            'Side Dish'
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
            
        self.stdout.write(self.style.SUCCESS('Successfully created categories')) 