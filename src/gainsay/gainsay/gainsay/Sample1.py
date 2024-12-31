"""
This will print the Applicant, every time it is changed
"""

L = "Sample1"

from applicants.models import Applicant

import logging as logger

def on_change(obj:Applicant, message:dict, subscription:dict):
    logger.info(f"{L}: Applicant Changed: {obj}")