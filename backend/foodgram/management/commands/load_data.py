import csv
import os

from django.core.management.base import BaseCommand

from foodgram.models import Ingredient


BASE_DIR = os.path.dirname(os.getcwd())
DATA_FILE = 'ingredients.csv'


class Command(BaseCommand):
    def import_movie_from_csv_file(self):
        data_folder = os.path.join(f'{BASE_DIR}/app/')
        print('!!!!', data_folder)
        with open(os.path.join(data_folder, DATA_FILE),
                  encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            for data_object in data:
                name = data_object[0]
                measurement_unit = data_object[1]

                try:
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit,
                    )
                    if created:
                        ingredient.save()
                        display_format = "\nИнгредиент, {}, сохранён."
                        print(display_format.format(ingredient))
                except Exception as ex:
                    print(str(ex))
                    msg = ("\n\nЧто-то пошло не так при сохранении"
                           " ингредиента: {}\n{}".format(name, str(ex)))
                    print(msg)

    def handle(self, *args, **options):
        """
        Вызывает функцию импорта данных из csv
        """
        self.import_movie_from_csv_file()
