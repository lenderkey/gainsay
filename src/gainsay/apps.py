from django.apps import AppConfig

import logging as logger

class GainsayConfig(AppConfig):
    name = 'gainsay'

    def ready(self):
        from .Gainsay import Gainsay
        from django.conf import settings

        ## if missing, will be picked up 
        GAINSAY = getattr(settings, "GAINSAY", {})
        if not GAINSAY:
            logger.warning(f"{self.name}: GAINSAY is not configured")
            return

        Gainsay.configure(
            url=GAINSAY.get("url"),
            root=GAINSAY.get("root"),
        )
