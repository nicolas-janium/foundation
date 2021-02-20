import logging
from datetime import datetime, timedelta
from uuid import uuid4
import os

from flask import redirect

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('dte_profile_redirect')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('dte_profile_redirect')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

PROJECT_ID = os.getenv('PROJECT_ID')
mtn_time = datetime.now() - timedelta(hours=7)

def main(request):
    args = request.args
    profile_url = args['redirect_url']
    contact_id = args['contact_id']

    session = Session()

    if source == 'connection':
        new_action = Action(str(uuid4()), contact_id, 8, mtn_time, None)
    elif source == 'message':
        new_action = Action(str(uuid4()), contact_id, 9, mtn_time, None)
    else:
        new_action = Action(str(uuid4()), contact_id, 10, mtn_time, None)
    session.add(new_action) # pylint: disable=no-member
    session.commit() # pylint: disable=no-member

    return redirect(profile_url)
