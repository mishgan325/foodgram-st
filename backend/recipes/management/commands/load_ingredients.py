import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загружает ингредиенты из JSON-файла в базу данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Путь к JSON-файлу с ингредиентами"
        )

    def handle(self, *args, **options):
        file_path = options["json_file"]

        try:
            with open(file_path, encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise CommandError(f"Файл не найден: {file_path}")
        except json.JSONDecodeError:
            raise CommandError("Некорректный формат JSON-файла")

        ingredients_to_create = []
        for item in data:
            name = item.get("name")
            unit = item.get("measurement_unit")

            if not name or not unit:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пропущен некорректный элемент: {item}"
                    )
                )
                continue

            if not Ingredient.objects.filter(
                name=name, measurement_unit=unit
            ).exists():
                ingredients_to_create.append(
                    Ingredient(name=name, measurement_unit=unit)
                )

        created = Ingredient.objects.bulk_create(ingredients_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Добавлено {len(created)} новых ингредиентов."
            )
        )
