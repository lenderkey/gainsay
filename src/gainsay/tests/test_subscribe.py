from django.test import TestCase

import gainsay
import datetime

import logging as logger

from . import __common as common

SUBSCRIBER_ID_1 = "test_subscribe_1"
SUBSCRIBER_ID_2 = "test_subscribe_2"

class TestSubscribe(common.Common, TestCase):
    """
    Test Subscribe / Unsubscribe
    """

    def test_subscribe_1(self):
        """
        Test Starting with no subscriptions
        """
        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 0)

        s2s = list(gainsay.subscriptions(SUBSCRIBER_ID_2))
        self.assertEqual(len(s2s), 0)

    def test_subscribe_2(self):
        """
        Test adding a few subscriptions
        """

        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_3)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 3)

        s2s = list(gainsay.subscriptions(SUBSCRIBER_ID_2))
        self.assertEqual(len(s2s), 0)

    def test_unsubscribe_1(self):
        """
        Test removing a subscription. 
        Also tests duplicates can be safely added
        """

        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_3)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_3)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 3)

        ## remove one
        gainsay.unsubscribe(SUBSCRIBER_ID_1, common.TABLE_ID_2)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 2)

        ## remove another
        gainsay.unsubscribe(SUBSCRIBER_ID_1, common.TABLE_ID_3)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 1)

        ## remove final
        gainsay.unsubscribe(SUBSCRIBER_ID_1, common.TABLE_ID)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 0)

    def test_unsubscribe_2(self):
        """
        Test removing non-existent subscriptions - should work
        """

        gainsay.unsubscribe(SUBSCRIBER_ID_1, common.TABLE_ID)
        gainsay.unsubscribe("XXX", common.TABLE_ID)
        gainsay.unsubscribe("YYY", common.TABLE_ID)
        gainsay.unsubscribe("ZZZ", "AAA")

    def test_unsubscribe_all(self):
        gainsay.unsubscribe_all(SUBSCRIBER_ID_1)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 0)

        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_2)
        gainsay.subscribe(SUBSCRIBER_ID_1, common.TABLE_ID_3)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 3)

        gainsay.unsubscribe_all(SUBSCRIBER_ID_1)

        s1s = list(gainsay.subscriptions(SUBSCRIBER_ID_1))
        self.assertEqual(len(s1s), 0)
