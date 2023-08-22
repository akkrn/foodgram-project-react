import base64
from http import HTTPStatus
from io import BytesIO
from urllib.parse import urlparse, urlsplit

import pyperclip
import requests

from recipes.models import Ingredient


def url_to_base64(url: str) -> str or None:
    response = requests.get(url)
    if response.status_code == HTTPStatus.OK:
        content_type = response.headers.get("content-type")
        if not content_type:
            path = urlparse(url).path
            ext = urlsplit(path)[1][1:]
        else:
            ext = content_type.split("/")[-1]
        encoded_data = base64.b64encode(response.content)
        base64_string = f"data:image/{ext};base64," + encoded_data.decode(
            "utf-8"
        )

        pyperclip.copy(base64_string)
        return base64_string
    return None


def generate_shopping_cart(ingredients: Ingredient) -> BytesIO:
    ingredients_str = (
        "Данный список покупок составлен в сервисе "
        "Foodgram\n\n"
        "Список покупок:"
    )
    for ingredient in ingredients:
        ingredient_name = ingredient[
            "recipe__recipes_ingredient__ingredient__name"
        ]
        total_amount = ingredient["total_amount"]
        measurement_unit = ingredient[
            "recipe__recipes_ingredient__ingredient__measurement_unit"
        ]
        ingredients_list = [
            f"{ingredient_name} - {total_amount} {measurement_unit}"
        ]
        ingredients_str += "\n" + "\n".join(ingredients_list)
    buffer = BytesIO()
    buffer.write(ingredients_str.encode())
    buffer.seek(0)
    return buffer
