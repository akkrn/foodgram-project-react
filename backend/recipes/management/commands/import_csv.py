import logging
from csv import DictReader
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

logging.basicConfig(
    level=logging.DEBUG,
    filename="main.log",
    filemode="w",
    format="%(asctime)s, %(levelname)s, %(message)s",
)


TABLES = {
    Ingredient: "ingredients.csv",
}


def generate_csv_headers(model: Any) -> list[str]:
    fields = model._meta.fields
    headers = [field.name for field in fields if field.name not in ["id"]]
    return headers


def transform_csv(model: Any, csv_path: str) -> None:
    headers = generate_csv_headers(model)
    with open(csv_path, "r", encoding="utf-8") as file:
        data = file.readlines()
        first_line = data[0].strip()

    if first_line == ",".join(headers):
        return

    with open(csv_path, "w", encoding="utf-8") as file:
        file.write(",".join(headers) + "\n")
        file.writelines(data)


class Command(BaseCommand):
    help = "Import from csv to db"

    def handle(self, *args, **kwargs) -> None:
        for (
            model,
            csv,
        ) in TABLES.items():
            transform_csv(model, settings.BASE_DIR / "data" / csv)
            with open(
                settings.BASE_DIR / "data" / csv, encoding="utf-8"
            ) as file:
                if model.objects.exists():
                    logging.error("Data already loaded... Exiting.")
                    continue
                reader = DictReader(file)
                model.objects.bulk_create(model(**data) for data in reader)
            self.stdout.write(self.style.SUCCESS("Data is loaded"))
