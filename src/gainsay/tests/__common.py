import time
import json

from threading import Thread
import logging as logger

TABLE_ID = "gainsay.models.Test"
TABLE_ID_1 = "gainsay.models.Test1"
TABLE_ID_2 = "gainsay.models.Test2"
TABLE_ID_3 = "gainsay.models.Test3"

class Common:
    def redis_connect(self) -> None:
        from django.conf import settings
        from gainsay import Gainsay

        Gainsay.configure(
            url=settings.GAINSAY.get("url"),
            root=settings.GAINSAY.get("root"),
        )
        
        self.connection = Gainsay.redis()
        if not self.connection:
            raise Exception("setUp: Redis is not configured")
        
        self.root = settings.GAINSAY.get("root", "gainsay")

    def listener_start(self) -> None:
        """    
        A thread is started to listen for messages.  Each test waits for a message
        to be received before continuing.
        
        The thread is terminated in tearDown by publishing a message to STOP
        """
        self.ready = False

        self.t = Thread(target=self.listener, daemon=True)
        self.t.start() 

        start = time.time()
        while not self.ready:
            if time.time() - start > 10.0:
                raise Exception("setUp: listener never became ready")
            
            time.sleep(0.1)

        self.received = []

    def clear(self):
        self.received = []
    
    def listener_stop(self) -> None:
        self.connection.publish(f"{self.root}/stop", "STOP")

    def listener(self):
        key = f"{self.root}/*"
        self.listener = self.connection.pubsub()
        self.listener.psubscribe(key)
        self.ready = True

        logger.info(f"listener: {key}")
        for message in self.listener.listen():
            if message.get("data") == b"STOP":
                break
            if message.get("type") not in [ "message", "pmessage" ]:
                continue

            self.received.append(json.loads(message.get("data")))

        print("thread done")

    def waitfor(self, obj_id:int=None, obj_pointer=None, delay:float=0.1, max_time:float=2.5, throw=True):
        start = time.time()
        while time.time() - start < max_time:
            for message in self.received:
                ## print(message)
                if obj_id is not None and message.get("obj_id") == obj_id:
                    return message
                if obj_pointer is not None and message.get("obj_pointer") == obj_pointer:
                    return message

            time.sleep(delay)

        if throw:
            raise Exception(f"waitfor: {obj_id} not received")
