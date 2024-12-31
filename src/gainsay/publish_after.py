#
#   gainsay/publish_after.py
#

def publish_after(f):
    """
    Decorate a function (typically 'save') that will publish a Gainsay event
    afterwards.

    Because code sometimes calls "save" through multiple passes, we don't
    trigger if the save is called within 0.5 seconds of the last save.
    """
    import time
    from .publish import publish
    from django.conf import settings

    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)

        if settings.EVENT_SUPPRESS:
            return result

        now = time.time()
        value = getattr(self, "__publish_after", None)
        if value and now - value < 0.5:
            return result
        
        self.__publish_after = now

        publish(self)

        return result

    return wrapper
