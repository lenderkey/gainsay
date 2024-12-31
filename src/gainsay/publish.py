#
#   gainsay/publish.py
#

from typing import Union
import json
import logging as logger

once_no_redis = False

from .protocols import GainsayProtocol

def publish(obj:GainsayProtocol) -> None:
    publish_raw(
        table_id=obj.obj_table_id(),
        obj_id=obj.obj_id(),
        obj_pointer=obj.obj_pointer(),
        extras=hasattr(obj, "obj_extras") and obj.obj_extras() or None,
    )

def publish_raw(table_id:str, obj_id:Union[str,int]=None, obj_pointer:str=None, extras:dict=None) -> None:
    """
    Publish a Gainsay event - prefer 'publish' over 'publish_raw' if possible
    """
    L = "gainsay.publish"

    from common.datetime import formatter_isodatetime # unnecessary (not accessed)
    from .Gainsay import Gainsay

    if not obj_pointer or not isinstance(obj_pointer, str):
        raise ValueError(f"{L}: obj_pointer is required and must be a string")

    connection = Gainsay.redis()
    if not connection:
        global once_no_redis
        if not once_no_redis:
            logger.warning(f"{L}: Redis is not configured")
            once_no_redis = True

        return

    message = {
        "table_id": table_id,
        "obj_id": obj_id,
        "obj_pointer": obj_pointer,
    }
    if extras:
        message["x"] = extras
    message = json.dumps(message)

    key = f"{Gainsay.root}/{table_id}"

    try:
        connection.publish(key, message)

        logger.debug(f"{L}: published {key}: {message}")
    except:
        logger.exception(f"{L}: failed to publish {key}: {message}")
