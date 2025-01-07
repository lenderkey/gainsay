#
#   Subscription
#   - track who wants information from Gainsay
#

from django.db import models
from ..constants import OBJ_TABLE_ID_LENGTH, SUBCRIBER_ID_LENGTH, OBJ_POINTER_LENGTH

class GainsaySubscription(models.Model):
    """
    You will rarely have to use this - prefer the top level functions
    """

    class Meta:
        unique_together = ("table_id", "subscriber_id")

    table_id = models.CharField(max_length=OBJ_TABLE_ID_LENGTH, null=False)
    subscriber_id = models.CharField(max_length=SUBCRIBER_ID_LENGTH, null=False)

    obj_pointer = models.CharField(max_length=OBJ_POINTER_LENGTH, null=True)
    obj_id = models.IntegerField(null=True)

    def __str__(self):
        return f"Subscription[{self.pk},table_id={self.table_id},subscriber_id={self.subscriber_id}]"
