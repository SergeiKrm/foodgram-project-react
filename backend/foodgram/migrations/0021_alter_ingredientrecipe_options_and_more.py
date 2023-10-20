# Generated by Django 4.1 on 2023-10-20 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0020_recipe_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецептах'},
        ),
        migrations.AlterModelOptions(
            name='tagrecipe',
            options={'verbose_name': 'Тег в рецепте', 'verbose_name_plural': 'Теги в рецептах'},
        ),
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_user_author',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_user_author', violation_error_message='Вы уже подписаны на этого автора!'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredient_recipe', violation_error_message='Ингредиент уже есть в рецепте!'),
        ),
        migrations.AddConstraint(
            model_name='tagrecipe',
            constraint=models.UniqueConstraint(fields=('tag', 'recipe'), name='unique_tag_recipe', violation_error_message='Тег уже есть в рецепте!'),
        ),
    ]