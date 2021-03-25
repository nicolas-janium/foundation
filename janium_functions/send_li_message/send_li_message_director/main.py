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

    logger = logging.getLogger('send_li_message_director')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *
    from janium_functions.send_li_message.send_li_message_function import main as function

    logger = logging.getLogger('send_li_message_director')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


def main(event, context):
    # Instantiates a Pub/Sub account
    publisher = pubsub_v1.PublisherClient()
    PROJECT_ID = os.getenv('PROJECT_ID')
    topic_path = publisher.topic_path(PROJECT_ID, 'janium-send-li-message-topic')

    session = get_session()

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    accounts = session.query(Account).filter(and_(
        and_(Account.effective_start_date < datetime.utcnow(), Account.effective_end_date > datetime.utcnow()),
        Account.is_sending_li_messages,
        Account.ulinc_config_id != Ulinc_config.unassigned_ulinc_config_id
    )).all()

    if now_date not in us_holidays:
        accounts_list = []
        for account in accounts:
            if account.ulinc_config.cookie_id != Cookie.unassigned_cookie_id:
                logger.debug(account.account_id)
                message_json = json.dumps(
                    {"data": {"account_id": account.account_id}}
                )
                message_bytes = message_json.encode('utf-8')

                # Publish message to send-li-message-topic ###
                try:
                    if not os.getenv('LOCAL_DEV'): ### Trigger send_li_message_function main ###
                        publish_future = publisher.publish(topic_path, data=message_bytes)
                        publish_future.result()
                    else: ### Trigger send_li_message_function main locally ###
                        payload = {"account_id": account.account_id}
                        payload = json.dumps(payload)
                        payload = base64.b64encode(str(payload).encode("utf-8"))
                        # return function.main({"data": payload}, 1)

                    accounts_list.append({"account_id": account.account_id})
                except Exception as err:
                    logger.error(str(err))
        logger.info('Messages to janium-send-li-message-topic published for accounts {}'.format(accounts_list))

if __name__ == '__main__':
    payload = {
        "from": "schedule"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
