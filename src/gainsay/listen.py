#
#   gainsay/listen.py
#

from typing import Callable, Union, List
import json
import logging as logger
from threading import Thread

from django.db import OperationalError

from .utils import formatter_isodatetime
from .protocols import GainsayProtocol

once_no_redis = False

def _send(
    message_data:Union[dict,None], 
    subscription:object, 
    callback:Callable[[dict, dict], Union[dict,GainsayProtocol,List[GainsayProtocol]]], 
    **ad,
) -> dict:
    L = "gainsay.listen/_send"
    
    subscription_data = {
        "table_id": subscription.table_id,
        "obj_pointer": subscription.obj_pointer,
        "obj_id": subscription.obj_id,
    }

    result_data = callback(message_data and dict(message_data), subscription_data, **ad)
    if not result_data:
        ## this may be None or an empty list
        return result_data

    ## if not a dict, it must be a GainsayProtocol or a list of GainSayProtocols 
    if isinstance(result_data, dict):
        pass
    else:
        ## the callback function may return a list of objects
        ## and we want to save the newest one
        if not isinstance(result_data, list):
            result_data = [ result_data ]

        first = result_data[0]
        best = {
            "table_id": subscription.table_id,
            "obj_id": first.obj_id(),
            "obj_pointer": first.obj_pointer(),
        }
        for rest in result_data[1:]:
            if formatter_isodatetime(rest.obj_pointer()) > formatter_isodatetime(best["obj_pointer"]):
                best["obj_id"] = rest.obj_id()
                best["obj_pointer"] = rest.obj_pointer()

        result_data = best
    
    ## note below uses 'result_data', not 'message_data' because
    ## the callback function may examine other objects
    is_changed = False

    obj_pointer = result_data.get("obj_pointer")
    if obj_pointer is not None:
        if obj_pointer != subscription.obj_pointer:
            subscription.obj_pointer = obj_pointer
            is_changed = True

    obj_id = result_data.get("obj_id")
    if obj_pointer is not None:
        if obj_id != subscription.obj_id:
            subscription.obj_id = obj_id
            is_changed = True

    if is_changed:
        try:
            subscription.save()
        except OperationalError as e:
            raise
        except:
            logger.exception(f"failed to save subscription {subscription.obj_pointer}/{subscription.obj_id}")
            ## raise

    return result_data

listener = None

## handlertsd is a dictionary of lists of tuples. Tuple is ( handler, subscription )
handlertsd = {}

def listen(
    subscriber_id:str, 
    callback:Callable[[dict, dict], Union[dict,GainsayProtocol,List[GainsayProtocol]]], 
    *,
    send_boot:bool=False,
    channel:str="all",
):
    """
    Listen for Gainsay events.
    If 'send_boot' is True, then the callback will be called with a None message
    when the function first starts, before any messages are received.
    """

    L = "gainsay.listen"
    
    from .Gainsay import Gainsay
    from .models import GainsaySubscription

    def _finished():
        for key in subscription_keys:
            handlerts = handlertsd.get(key)
            if not handlerts:
                continue

            handlertsd[key] = [ (handler, subscription) for handler, subscription in handlerts if handler != _message_handler ]

    connection = Gainsay.redis()
    if not connection:
        global once_no_redis
        if not once_no_redis:
            logger.warning(f"{L}: Redis is not configured")
            once_no_redis = True

        return

    global listener, handlertsd
    if not listener:
        listener = connection.pubsub()
        listener.psubscribe(f"{Gainsay.root}/{channel}/*")

        def do_listen():
            for message in listener.listen():
                channel = message.get("channel")
                if not channel:
                    continue

                channel = channel.decode("utf-8")

                handlerts = handlertsd.get(channel)
                for handler, subscription in handlerts or []:
                    handler(message, subscription)

        listen_thread = Thread(target=do_listen, daemon=True)
        listen_thread.start() 

    ## highly dependendent on the closure!
    def _message_handler(message:dict, subscrption:GainsaySubscription|None=None):
        type = message.get("type")
        if type not in [ "message", "pmessage" ]:
            return

        message_data = json.loads(message.get("data"))
        if not isinstance(message_data, dict):
            return

        if message_data.get("command") == "unlisten":
            logger.info(f"{L}: {subscriber_id=} done because command=unlisten")
            _finished()
            return
        
        if not subscription:
            return

        if subscription.obj_pointer and formatter_isodatetime(subscription.obj_pointer) >= message_data["obj_pointer"]:
            logger.debug(
                f"{L}: {subscriber_id=} skipping because obj_pointer is old"
                f" sub={formatter_isodatetime(subscription.obj_pointer)}"
                f' msg={message_data["obj_pointer"]}'
            )
            return

        if _send(message_data, subscription, callback) is None:
            logger.info(f"{L}: {subscriber_id=} done because callback returned None")
            _finished()
            return

    ## get subscriptions
    subscription_keys = []
    for subscription in GainsaySubscription.objects.filter(subscriber_id=subscriber_id):
        subscription_key = f"{Gainsay.root}/{subscription.table_id}"
        subscription_keys.append(subscription_key)        
        handlertsd.setdefault(subscription_key, []).append((_message_handler, subscription))
        logger.debug(f"{L}: subscribe to '{subscription_key}': {subscription}")

        if send_boot:
            _send(None, subscription, callback)

    if not subscription_keys:
        logger.info(f"{L}: {subscriber_id=} done because no subscriptions")
        _finished()

    ## control commands (especially unlisten)
    subscription_key = f"{Gainsay.root}/commands/{subscriber_id}"
    subscription_keys.append(subscription_key)        
    handlertsd.setdefault(subscription_key, []).append((_message_handler, None))

def unlisten(subscriber_id:str):
    """
    Note this is sent from unsubscribe_all
    """
    L = "unlisten"

    from .Gainsay import Gainsay

    connection = Gainsay.redis()
    if not connection:
        return

    message = json.dumps({
        "command": "unlisten",
        "subscriber_id": subscriber_id,
    })

    key = f"{Gainsay.root}/commands/{subscriber_id}"
    print("UNLISTEN", key)

    connection.publish(key, message)
