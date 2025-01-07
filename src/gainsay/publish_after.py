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

        if getattr(settings, "EVENT_SUPPRESS", False):
            return result

        now = time.time()
        value = getattr(self, "__publish_after", None)
        if value and now - value < 0.5:
            return result
        
        self.__publish_after = now

        publish(self)

        return result

    return wrapper

def update_timestamp(key="last_updated", **ad):
    """
    Decorator to update a timestamp field on a model instance
    when it is saved. You need to add `@gainsay.update_timestamp()`
    in front of the `save()` method of the model.
    """
    from django.conf import settings

    def inner_decorator(f):
        def wrapped(self, *args, **kwargs):
            from django.utils import timezone

            if not getattr(settings, "EVENT_SUPPRESS", False):
                setattr(self, key, timezone.now())

            result = f(self, *args, **kwargs)
            return result

        return wrapped

    return inner_decorator