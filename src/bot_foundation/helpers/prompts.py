import os
import json

from InquirerPy import inquirer
from InquirerPy.utils import patched_print
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


BASEDIR = os.path.abspath(os.path.dirname(__file__))


def new_config():
    result_prefix = inquirer.text(
        message="Which character do you want your bot commands to be prefixed with >>> ",
        validate=lambda result: len(result) == 1,
        invalid_message="Length of answers should be 1 character!"
    ).execute()
    
    
