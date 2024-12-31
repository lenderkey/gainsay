from django.test import SimpleTestCase

import gainsay
import datetime

import logging as logger

from . import __common as common

# class MyTestClass:
#     def __init__(self, pk, last_updated):
#         self.pk = pk
#         self.last_updated = last_updated

#         self.alt_pk_1 = 1
#         self.alt_pk_2 = 2

#         self.alt_obj_pointer_1 = "2020-01-01T00:11:00.000Z"
#         self.alt_obj_pointer_2 = "2020-01-01T00:12:00.000Z"

#     @gainsay.publish_after(common.TABLE_ID) ## really should be ...something...MyTestClass
#     def save_0(self):
#         pass

#     @gainsay.publish_after(common.TABLE_ID, obj_id="alt_pk_1", obj_pointer="alt_obj_pointer_1")
#     def save_1(self):
#         pass

#     @gainsay.publish_after(common.TABLE_ID, obj_id="alt_pk_2", obj_pointer="alt_obj_pointer_2")
#     def save_2(self):
#         pass

#     @gainsay.publish_after(common.TABLE_ID, obj_id=None, obj_pointer="alt_obj_pointer_2")
#     def save_3(self):
#         pass

#     @gainsay.publish_after(common.TABLE_ID, obj_id="alt_pk_2", obj_pointer=None)
#     def save_4(self):
#         pass

# class TestPublishAfter(common.Common, SimpleTestCase):
#     """
#     Test the publish_after decorator.
#     """
#     def setUp(self) -> None:
#         self.redis_connect()
#         self.listener_start()

#     def tearDown(self) -> None:
#         self.listener_stop()

#         return super().tearDown()

#     def test_standard_1(self):
#         """Test standard obj_id and obj_pointer"""
#         OBJ_ID = 11
#         t = MyTestClass(pk=OBJ_ID, last_updated="2020-01-01T00:11:00Z")
#         t.save_0()
#         self.waitfor(obj_id=OBJ_ID)

#     def test_alt_1(self):
#         """Test different obj_id and obj_pointer"""
#         OBJ_ID = 12
#         t = MyTestClass(pk=OBJ_ID, last_updated="2020-01-01T00:12:00Z")
#         t.save_1()
#         message = self.waitfor(obj_id=t.alt_pk_1)
#         self.assertEqual(message.get("obj_id"), t.alt_pk_1)
#         self.assertEqual(message.get("obj_pointer"), t.alt_obj_pointer_1)

#     def test_alt_2(self):
#         """Test different obj_id and obj_pointer"""
#         OBJ_ID = 13
#         t = MyTestClass(pk=OBJ_ID, last_updated="2020-01-01T00:13:00Z")
#         t.save_2()
#         message = self.waitfor(obj_id=t.alt_pk_2)
#         self.assertEqual(message.get("obj_id"), t.alt_pk_2)
#         self.assertEqual(message.get("obj_pointer"), t.alt_obj_pointer_2)

#     def test_optional_obj_id(self):
#         """Test optional obj_id"""
#         OBJ_ID = 14
#         t = MyTestClass(pk=OBJ_ID, last_updated="2020-01-01T00:14:00Z")
#         t.save_3()
#         message = self.waitfor(obj_pointer=t.alt_obj_pointer_2)
#         self.assertIsNone(message.get("obj_id"))
#         self.assertEqual(message.get("obj_pointer"), t.alt_obj_pointer_2)

#     def test_optional_obj_pointer(self):
#         """Test optional obj_pointer"""
#         OBJ_ID = 15
#         t = MyTestClass(pk=OBJ_ID, last_updated="2020-01-01T00:15:00Z")
#         t.save_4()
#         message = self.waitfor(obj_id=t.alt_pk_2)
#         self.assertEqual(message.get("obj_id"), t.alt_pk_2)
#         self.assertIsNone(message.get("obj_pointer"))
        
