from django.test import TransactionTestCase

import gainsay
import datetime
import time

import logging as logger

from . import __common as common

SUBSCRIBER_ID_1 = "test_subscribe_1"
SUBSCRIBER_ID_2 = "test_subscribe_2"
SUBSCRIBER_ID_3 = "test_subscribe_3"

class TestListen(common.Common, TransactionTestCase):
    """
    Test Subscribe / Unsubscribe
    """

    def setUp(self) -> None:
        self.received = []
        return super().setUp()

    def test_subscribe_1(self):
        """
        Test Starting with no subscriptions
        """
        def listen_in(data, subd, **ad):
            self.received.append(data)
            return data

        gainsay.unsubscribe_all(SUBSCRIBER_ID_1)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_1)
        gainsay.listen(SUBSCRIBER_ID_1, listen_in)

        ## publish and see it
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_1, obj_id=1, obj_pointer="2020-01-01T00:00:00.000Z")
        self.waitfor(obj_id=1)

        ## the same ID should come through
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_1, obj_id=1, obj_pointer="2020-01-01T00:00:01.000Z")
        self.waitfor(obj_id=1)

        ## old obj_pointer should not come through
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_1, obj_id=2, obj_pointer="1999-01-01T00:00:00.000Z")
        message = self.waitfor(obj_id=1, throw=False)
        self.assertIsNone(message)

        ## new obj_pointer should come through
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_1, obj_id=3, obj_pointer="2020-01-01T00:00:02.000Z")
        self.waitfor(obj_id=3)
        self.assertIsNone(message)

        ## resubscribing should return highest obj_pointer
        sd = gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_1)
        self.assertEqual(sd["obj_pointer"], "2020-01-01T00:00:02.000Z")
        self.assertEqual(sd["obj_id"], 3)
        
    def test_subscribe_2(self):
        """
        Test blocking future messages inside the listener
        """
        def listen_in(data, subd, **ad):
            self.received.append(data)
            data["obj_pointer"] = "2099-01-01T00:00:02.000Z"

        gainsay.unsubscribe_all(SUBSCRIBER_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_2, common.TABLE_ID_2)
        gainsay.listen(SUBSCRIBER_ID_2, listen_in)

        ## publish and see it
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_2, obj_id=1, obj_pointer="2020-01-01T00:00:00.000Z")
        self.waitfor(obj_id=1)

        ## future object is blocked because the listener
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_2, obj_id=1, obj_pointer="2020-01-01T00:00:01.000Z")
        sd = self.waitfor(obj_id=1, throw=False)
        self.assertIsNone(sd)

        
    def test_subscribe_3(self):
        """
        Test turning off the listener
        """
        def listen_in(data, subd, **ad):
            self.received.append(data)
            return ## this is what turns it off

        gainsay.unsubscribe_all(SUBSCRIBER_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_2, common.TABLE_ID_2)
        gainsay.listen(SUBSCRIBER_ID_2, listen_in)

        ## publish and see it
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_2, obj_id=1, obj_pointer="2020-01-01T00:00:00.000Z")
        self.waitfor(obj_id=1)

        ## future object is blocked because the listener is turned off
        self.clear()
        gainsay.publish_raw(common.TABLE_ID_2, obj_id=1, obj_pointer="2100-01-01T00:00:01.000Z")
        sd = self.waitfor(obj_id=1, throw=False)
        self.assertIsNone(sd)
