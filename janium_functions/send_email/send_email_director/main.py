import base64
import json
from datetime import datetime
import logging
import sys
import os
import pytz

import holidays
from google.cloud import pubsub_v1
from sqlalchemy import and_, or_

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('send_email_director')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *
    from janium_functions.send_email.send_email_function import main as function

    logger = logging.getLogger('send_email_director')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

PROJECT_ID = os.getenv('PROJECT_ID')

mtn_tz = pytz.timezone('US/Mountain')
mtn_time = datetime.now(pytz.timezone('UTC')).astimezone(mtn_tz)

def main(event, context):
    # Instantiates a Pub/Sub account
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, 'janium-send-email-topic')

    session = get_session()

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    accounts = session.query(Account).filter(and_(
        and_(Account.effective_start_date < mtn_time, Account.effective_end_date > mtn_time),
        Account.is_sending_emails,
        Account.email_config_id != Email_config.unassigned_email_config_id
    )).all()

    if now_date not in us_holidays:
        accounts_list = []
        for account in accounts:
            message_json = json.dumps(
                {"data": {"account_id": account.account_id}}
            )
            message_bytes = message_json.encode('utf-8')

            ### Publish message to send-dte-function ###
            try:
                if not os.getenv('LOCAL_DEV'):
                    publish_future = publisher.publish(topic_path, data=message_bytes)
                    publish_future.result()
                else:
                    payload = {"account_id": account.account_id}
                    payload = json.dumps(payload)
                    payload = base64.b64encode(str(payload).encode("utf-8"))
                    # function.main({"data": payload}, 1)
                accounts_list.append({"account_id": account.account_id})
            except Exception as err:
                logger.error(str(err))
        logger.info('Messages to janium-send-email-topic published for accounts {}'.format(accounts_list))

if __name__ == '__main__':
    payload = {
        "testing": "true"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
