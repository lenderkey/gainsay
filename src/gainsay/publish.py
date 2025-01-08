#
#   gainsay/publish.py
#

from typing import Union, List
import json
import logging as logger
import datetime

once_no_redis = False

from .protocols import GainsayProtocol

def publish(obj:GainsayProtocol) -> None:
    publish_raw(
        table_id=obj.obj_table_id(),
        obj_id=obj.obj_id(),
        obj_pointer=obj.obj_pointer(),
        obj_channels=hasattr(obj, "obj_channels") and obj.obj_channels() or None,
        extras=hasattr(obj, "obj_extras") and obj.obj_extras() or None,
    )

def publish_raw(
    table_id:str, 
    obj_id:Union[str,int]=None, 
    obj_pointer:Union[str,datetime.datetime]=None, 
    obj_channels:List[Union[str,int]]=None, 
    extras:dict=None,
) -> None:
    """
    Publish a Gainsay event - prefer 'publish' over 'publish_raw' if possible
    """
    L = "gainsay.publish"

    from .Gainsay import Gainsay
    from .helpers import formatter_isodatetime

    if not obj_pointer:
        raise ValueError(f"{L}: obj_pointer is required")
    elif isinstance(obj_pointer, datetime.datetime):
        obj_pointer = formatter_isodatetime(obj_pointer)
    elif isinstance(obj_pointer, str):
        pass
    else:
        raise ValueError(f"{L}: obj_pointer is required and must be a string or datetime")

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

    for key in [ "all", *(obj_channels or []) ]:
        key = f"{Gainsay.root}/{key}/{table_id}"

        try:
            connection.publish(key, message)

            logger.debug(f"{L}: published {key}: {message}")
        except:
            logger.exception(f"{L}: failed to publish {key}: {message}")

    # key = f"{Gainsay.root}/{table_id}"

    # try:
    #     connection.publish(key, message)

    #     logger.debug(f"{L}: published {key}: {message}")
    # except:
    #     logger.exception(f"{L}: failed to publish {key}: {message}")
