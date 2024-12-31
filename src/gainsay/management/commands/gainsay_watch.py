from typing import List

import importlib.util
import sys
import os
import time
import hashlib
import glob
import signal

from icecream import ic

from django.core.management.base import BaseCommand
from django.db import OperationalError

import logging as logger

L = "gainsay_watch"

def load_module_from_file(file_path):
    # Get the module name from the file path
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Check if the module is already loaded
    if module_name in sys.modules:
        return sys.modules[module_name]

    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class Command(BaseCommand):
    help = """Watch on Gainsay events and execute actions"""

    def add_arguments(self, parser):
        ## takes N folders or filenames as arguments
        parser.add_argument(
            "filename",
            nargs="*",
            type=str,
            help="watch files (must by *.py or folders)",
        )

    def handle(self, filename:List[str], *args, **kwargs):
        """
        Filename can be a folder or a file. It can be a Glob also. And it can use ~ for home."""
        L = "Command.handle"

        self.subscribed = set()

        for pattern in filename:
            pattern = os.path.expanduser(pattern)

            for fn in glob.glob(pattern):
                if os.path.isdir(fn):
                    for root, dirs, files in os.walk(fn):
                        for f in files:
                            if f.endswith(".py"):
                                self.watch(f"{root}/{f}")
                elif os.path.isfile(fn) and fn.endswith(".py"):
                    self.watch(fn)
                else:
                    logger.error(f"{L}: {fn} is not a Python file or folder")

        while True:
            logger.info(f"{L}: sleeping")
            time.sleep(60)

    def watch(self, filename:str):
        import gainsay
        from common.enum import SUBCRIBER_ID_LENGTH

        L = "watch"

        logger.info(f"{L}: watching {filename}")

        ## load the python file as a module
        M = load_module_from_file(filename)
        
        subscription_id = hashlib.md5(filename.encode()).hexdigest()
        subscription_id += "-" + os.path.basename(filename[:-3])
        subscription_id = subscription_id[:SUBCRIBER_ID_LENGTH]

        on_change = getattr(M, "on_change", None)
        if not on_change:
            logger.error(f"{L}: {filename}: no 'on_change'")
            return

        ad = on_change.__annotations__
        if not ad or not "obj" in ad:
            logger.error(f"{L}: {filename}: 'on_change' has no 'obj' annotation")
            return
        
        cls = ad["obj"]
        if not hasattr(cls, "obj_table_id"):
            logger.error(f"{L}: {filename}: 'obj' has no 'obj_table_id' - cannot subscribe")
            return
        
        if subscription_id in self.subscribed:
            logger.warning(f"{L}: {filename}: already subscribed")
            return
        else:
            self.subscribed.add(subscription_id)

        table_id = cls.obj_table_id(None)
        last_obj_id = None
        last_time = 0

        def handler(message:dict, subscription:dict, **ad):
            nonlocal last_obj_id, last_time
            
            try:
                for x in range(1):
                    if not message:
                        break
                    
                    obj_id = message["obj_id"]
                    if last_obj_id == obj_id and time.time() - last_time < 0.5:
                        break

                    obj = cls.by_id(obj_id)
                    if not obj:
                        break

                    ## gainsay is sending last object on boot
                    ## not sure if this is an error
                    obj_pointer = message.get("obj_pointer")
                    subscription_obj_pointer = subscription.get("obj_pointer")
                    if obj_pointer and obj_pointer == subscription_obj_pointer:
                        break

                    last_obj_id = obj_id
                    last_time = time.time()

                    on_change(obj, message=message, subscription=subscription)

                    # ic(L, message, obj)

                return message
            except OperationalError:
                DELAY = 10

                logger.exception(f"{L}: OperationalError")
                logger.fatal(f"{L}:-- killing process in {DELAY} seconds...")
                time.sleep(DELAY)

                current_pid = os.getpid()
                os.kill(current_pid, signal.SIGKILL)

        subd = gainsay.subscribe(subscription_id, table_id)
        logger.info(f"{L}: SUBSCRIBE: {subscription_id=} {table_id=} {subd=}")

        gainsay.listen(
            subscription_id,
            handler,
            send_boot=False,    
        )
        
        

