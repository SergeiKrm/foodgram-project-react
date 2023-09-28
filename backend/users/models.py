from django.contrib.auth.models import AbstractUser
from django.db import models

'''
class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Уникальный юзернейм'
        #validators=[character_validator] написать еще надо его   ^[\w.@+-]+\z
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия'
    )

    class Meta:
        # ordering = ('username',)
        verbose_name = 'Пользователь'

    def __str__(self):
        return (self.get_full_name()
                if (self.first_name and self.last_name) else self.username)'''