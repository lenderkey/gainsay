import sys
import yaml
import json

from django.core.management.base import BaseCommand

import logging as logger

L = "gainsay_snoop"

class Command(BaseCommand):
    help = """Snoop on Gainsay events"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--table-id", 
            help="only load this table", 
            dest="table_id",
            required=False,
        )
        parser.add_argument(
            "--deep",
            help="deep inspection",
            dest="is_deep",
            action="store_true",
        )

    def handle(self, table_id:str, is_deep:bool, *args, **kwargs):
        from gainsay.bl import snoop

        def callback(data):
            print("---")
            print(yaml.dump(data))

        snoop(table_id=table_id, is_deep=is_deep, callback=callback)

    def OLD_handle(self, table_id:str, is_deep:bool, *args, **kwargs):
        L = "Command.handle"

        from gainsay import Gainsay

        connection = Gainsay.redis()
        if not connection:
            logger.fatal(f"{L}: Redis is not configured")
            sys.exit(1)

        key = f"{Gainsay.root}/{table_id or '*'}"

        listener = connection.pubsub()

        if table_id:
            listener.subscribe(key)
        else:
            listener.psubscribe(key)

        try:
            for message in listener.listen():
                if is_deep:
                    try:
                        message["data"] = json.loads(message.get("data"))
                    except:
                        pass

                    print("---")
                    print(yaml.dump(message))
                else:
                    type = message.get("type")
                    if type in [ "message", "pmessage" ]:
                        data = json.loads(message.get("data"))

                        print("---")
                        print(yaml.dump(data))
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            logger.exception(f"{L}: unexpected error")
            sys.exit(1)
