# Generated by Django 5.1.7 on 2025-03-29 22:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_recipe'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Recipe',
        ),
    ]
