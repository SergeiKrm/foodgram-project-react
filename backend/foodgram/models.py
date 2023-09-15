from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()




class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
        )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX',
        null=True,
        unique=True,
        )   # Цветовой код, например, #49B64E.

    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        null=True,
        unique=True,
        )

    class Meta:
        verbose_name = ('Тег')
        verbose_name_plural = ('Теги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):   # добавить поле Количество
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        )

    class Meta:
        verbose_name = ('Ингредиент')
        verbose_name_plural = ('Ингредиенты')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        )
    # image - required string <binary> Картинка, закодированная в Base64
    text = models.TextField(verbose_name='Описание',)
    ingredients = models.ForeignKey(Ingredient, verbose_name='Список ингредиентов', on_delete=models.CASCADE)
      # с выбором из предустановленного списка
      # и с указанием количества и единицы измерения.
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='Список id тегов',) #1toMany
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления в мин',
        )

    class Meta:
        # ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


