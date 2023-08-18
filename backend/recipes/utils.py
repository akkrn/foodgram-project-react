import requests
import base64
import pyperclip
from urllib.parse import urlparse, urlsplit


def url_to_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        content_type = response.headers.get('content-type')
        if not content_type:
            path = urlparse(url).path
            ext = urlsplit(path)[1][1:]
        else:
            ext = content_type.split('/')[-1]
        encoded_data = base64.b64encode(response.content)
        base64_string = f"data:image/{ext};base64," + encoded_data.decode(
            "utf-8")

        pyperclip.copy(base64_string)
        print("Base64 строка скопирована в буфер обмена!")
        return base64_string
    else:
        print(f"Ошибка {response.status_code}: Не получилось достать "
              f"изображение.")
        return None

image_url = "https://www.gastronom.ru/binfiles/images/20230421/b5aa6302.jpg"
base64_string = url_to_base64(image_url)
