import logging
from csv import DictReader

from django.core.management.base import BaseCommand

from ...models import Ingredient

logging.basicConfig(
    level=logging.DEBUG,
    filename="main.log",
    filemode="w",
    format="%(asctime)s, %(levelname)s, %(message)s",
)


TABLES = {
    Ingredient: "ingredients.csv",
}


def generate_csv_headers(model):
    fields = model._meta.fields
    headers = [field.name for field in fields if field.name not in ["id"]]
    return headers


def transform_csv(model, csv_path):
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

    def handle(self, *args, **kwargs):
        for (
            model,
            csv,
        ) in TABLES.items():
            transform_csv(model, f"../data/{csv}")
            with open(f"../data/{csv}", encoding="utf-8") as file:
                if model.objects.exists():
                    logging.error("Data already loaded... Exiting.")
                    continue
                reader = DictReader(file)
                model.objects.bulk_create(model(**data) for data in reader)
            self.stdout.write(self.style.SUCCESS("Data is loaded"))
