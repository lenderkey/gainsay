#
#   gainsay/subscribe.py
#

def subscribe(subscriber_id, table_id):
    """
    """

    from .models import GainsaySubscription
    from django.core.exceptions import ObjectDoesNotExist

    try:
        subscription = GainsaySubscription.objects.get(subscriber_id=subscriber_id, table_id=table_id)
    except ObjectDoesNotExist:
        subscription = GainsaySubscription(subscriber_id=subscriber_id, table_id=table_id)
        subscription.save()

    return {
        "table_id": table_id,
        "obj_pointer": subscription.obj_pointer,
        "obj_id": subscription.obj_id,
    }

def subscriptions(subscriber_id):
    """
    """

    from .models import GainsaySubscription
    from django.core.exceptions import ObjectDoesNotExist

    subscriptions = GainsaySubscription.objects.filter(subscriber_id=subscriber_id)
    for subscription in subscriptions:
        yield {
            "table_id": subscription.table_id,
            "obj_pointer": subscription.obj_pointer,
            "obj_id": subscription.obj_id,
        }

def unsubscribe(subscriber_id, table_id):
    """
    """

    from .models import GainsaySubscription
    from django.core.exceptions import ObjectDoesNotExist

    try:
        subscription = GainsaySubscription.objects.get(subscriber_id=subscriber_id, table_id=table_id)
        subscription.delete()
    except ObjectDoesNotExist:
        pass

def unsubscribe_all(subscriber_id):
    """
    """

    from .listen import unlisten
    from .models import GainsaySubscription
    from django.core.exceptions import ObjectDoesNotExist

    subscriptions = GainsaySubscription.objects.filter(subscriber_id=subscriber_id)
    for subscription in subscriptions:
        try:
            subscription.delete()
        except ObjectDoesNotExist:
            pass

    unlisten(subscriber_id)