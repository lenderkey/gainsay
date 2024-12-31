from django.test import SimpleTestCase
from unittest.mock import patch

import gainsay
import datetime

import logging as logger

from . import __common as common

def mock_no_redis():
    return

class TestNoRedis(common.Common, SimpleTestCase):
    """
    Test having no redis - should not crash.

    These could be improved to check for the warning messages
    or whatever, but coverage is good enough for now.
    """

    @patch("gainsay.Gainsay.Gainsay.redis", mock_no_redis)
    def test_publish(self):
        gainsay.publish_raw(common.TABLE_ID, obj_id=1, obj_pointer="2020-01-01T00:11:00Z")


    @patch("gainsay.Gainsay.Gainsay.redis", mock_no_redis)
    def test_listen(self):
        def somecallback():
            pass

        gainsay.listen("XXX", somecallback)

