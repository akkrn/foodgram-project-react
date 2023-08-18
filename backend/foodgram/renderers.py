from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"
    charset = "iso-8859-1"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            data = str(data)
        return data.encode(self.charset)