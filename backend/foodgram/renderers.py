from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"
    charset = "utf-8"

    def render(
        self, data: dict, media_type=None, renderer_context=None
    ) -> bytes:
        if isinstance(data, dict):
            data = str(data)
        return data.encode(self.charset)
