# Generated by Django 4.1 on 2023-09-24 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0006_alter_recipe_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
    ]