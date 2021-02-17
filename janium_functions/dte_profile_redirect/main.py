from flask import redirect
from db_model import *
from datetime import datetime, timedelta
from uuid import uuid4
import logging

if not os.getenv('LOCAL_DEV'):
    logger = logging.getLogger('dte_profile_redirect')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logger = logging.getLogger('dte_profile_redirect')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


def main(request):
    args = request.args
    profile_url = args['redirect_url']
    contactid = args['contactid']

    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    if source == 'connection':
        new_action = Action(str(uuid4()), contactid, 8, datetime.now() - timedelta(hours=7), None)
    elif source == 'message':
        new_action = Action(str(uuid4()), contactid, 9, datetime.now() - timedelta(hours=7), None)
    else:
        new_action = Action(str(uuid4()), contactid, 10, datetime.now() - timedelta(hours=7), None)
    session.add(new_activity) # pylint: disable=no-member
    session.commit() # pylint: disable=no-member

    return redirect(profile_url)
