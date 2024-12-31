from typing import Callable
from gainsay import Gainsay

import json
import logging as logger

def snoop(callback:Callable, *, connection=None, table_id:str=None, is_deep:bool=False):
    connection = Gainsay.redis()
    if not connection:
        raise Exception("Redis is not configured")

    key = f"{Gainsay.root}/{table_id or '*'}"

    listener = connection.pubsub()

    if table_id:
        listener.subscribe(key)
    else:
        listener.psubscribe(key)

    for message in listener.listen():
        if is_deep:
            try:
                message["data"] = json.loads(message.get("data"))
            except:
                pass

            callback(message)
        else:
            type = message.get("type")
            if type in [ "message", "pmessage" ]:
                data = json.loads(message.get("data"))
                callback(data)

def snoop_daemon(callback:Callable, **kwargs):
    import threading

    def run():
        snoop(callback, **kwargs)

    threading.Thread(target=run).start()