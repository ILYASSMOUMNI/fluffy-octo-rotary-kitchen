# Generated by Django 4.2.20 on 2025-04-23 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('admin', 'Admin'), ('chef', 'Chef'), ('blogueur', 'Blogueur')], max_length=20),
        ),
    ]
