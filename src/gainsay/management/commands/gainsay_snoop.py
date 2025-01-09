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
            "--channel", 
            help="listen on this cannel", 
            dest="channel",
            default="all",
            required=False,
        )
        parser.add_argument(
            "--deep",
            help="deep inspection",
            dest="is_deep",
            action="store_true",
        )

    def handle(self, table_id:str, is_deep:bool, channel: str, *args, **kwargs):
        from gainsay.bl import snoop

        def callback(data, channel, table_id, **kwargs):
            print("---")
            print(yaml.dump(data))

        snoop(table_id=table_id, is_deep=is_deep, channel=channel, callback=callback)

