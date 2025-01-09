from typing import Callable, Dict
from gainsay import Gainsay

import json
import logging as logger

def snoop(callback:Callable, *, connection=None, table_id:str=None, channel: str="all", is_deep:bool=False):
    connection = Gainsay.redis()
    if not connection:
        raise Exception("Redis is not configured")

    key = f"{Gainsay.root}/{channel}/{table_id or '*'}"
    logger.info(f"snooping on {key}")

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

            callback(message, channel=channel, table_id=table_id)
        else:
            type = message.get("type")
            if type in [ "message", "pmessage" ]:
                data = json.loads(message.get("data"))
                callback(data, channel=channel, table_id=table_id)

def snoop_daemon(callback:Callable, **kwargs):
    import threading

    def run():
        snoop(callback, **kwargs)

    threading.Thread(target=run).start()