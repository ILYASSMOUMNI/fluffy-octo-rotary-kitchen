from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_recipe_servings'),
    ]

    operations = [
        # Alter the category field to be a ForeignKey to the Category model
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=models.ForeignKey(
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='recipes', 
                to='recipes.category'
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='servings',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
