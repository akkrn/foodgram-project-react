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


class Command(BaseCommand):
    help = "Import from csv to db"

    def handle(self, *args, **kwargs):
        for model, csv in TABLES.items():
            try:
                with open(f"./data/{csv}", encoding="utf-8") as file:
                    if model.objects.exists():
                        logging.error("Data already loaded... Exiting.")
                        continue
                    reader = DictReader(file)
                    model.objects.bulk_create(model(**data) for data in reader)
                    logging.info(f"Data for {model.__name__} is loaded")
                    self.stdout.write(self.style.SUCCESS("Data is loaded"))
            except Exception as e:
                logging.error(f"Error loading data for {model.__name__}: {e}")
