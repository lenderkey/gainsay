from django.test import SimpleTestCase

import gainsay
import datetime

import logging as logger

from . import __common as common

class TestPublish(common.Common, SimpleTestCase):
    """
    Test the publish command.
    """
    def setUp(self) -> None:
        self.redis_connect()
        self.listener_start()

    def tearDown(self) -> None:
        self.listener_stop()

        return super().tearDown()

    def test_both_1(self):
        """
        Test that a message is published and received
        """
        OBJ_ID = 11
        gainsay.publish_raw(common.TABLE_ID, obj_id=OBJ_ID, obj_pointer="2020-01-01T00:11:00Z")
        self.waitfor(obj_id=OBJ_ID)

    def test_both_2(self):
        """
        Test that a message is published and received - second time
        """
        OBJ_ID = 12
        gainsay.publish_raw(common.TABLE_ID, obj_id=OBJ_ID, obj_pointer="2020-01-01T00:12:00Z")
        self.waitfor(obj_id=OBJ_ID)

    def test_extras(self):
        """
        Test that a message can take extras
        """
        OBJ_ID = 21
        gainsay.publish_raw(common.TABLE_ID, obj_id=OBJ_ID, obj_pointer="2020-01-01T00:21:00Z", extras={
            "foo": "bar",
        })
        message = self.waitfor(obj_id=OBJ_ID)
        self.assertEqual(message.get("foo"), "bar")

    def test_obj_id_only(self):
        """
        obj_id only
        """
        OBJ_ID = 31
        gainsay.publish_raw(common.TABLE_ID, obj_id=OBJ_ID, obj_pointer="2020-01-01T00:31:00Z")
        self.waitfor(obj_id=OBJ_ID)

    def test_obj_pointer_only(self):
        """
        obj_pointer only
        """
        TIMESTAMP = "2020-01-01T00:41:00Z"
        gainsay.publish_raw(common.TABLE_ID, obj_pointer=TIMESTAMP)
        self.waitfor(obj_pointer=TIMESTAMP)

    def test_fail_missing_both(self):
        """
        Fail if both obj_id and obj_pointer are missing
        """
        with self.assertRaises(ValueError):
            gainsay.publish_raw(common.TABLE_ID)

    def test_fail_naive_datetime(self):
        """
        Fail if obj_pointer is naive
        """
        OBJ_ID = 51
        with self.assertRaises(ValueError):
            gainsay.publish_raw(common.TABLE_ID, obj_id=OBJ_ID, obj_pointer=datetime.datetime.now())