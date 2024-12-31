from django.apps import AppConfig

class GainsayConfig(AppConfig):
    name = 'gainsay'

    def ready(self):
        from .Gainsay import Gainsay
        from django.conf import settings

        Gainsay.configure(
            url=settings.GAINSAY.get("url"),
            root=settings.GAINSAY.get("root"),
        )
