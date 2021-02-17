import base64
import json
from datetime import datetime
import logging
import sys
import os

import holidays
from google.cloud import pubsub_v1
from sqlalchemy import and_, or_

# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = 'janium-foundation'

if not os.getenv('LOCAL_DEV'):
    from db_model import *

    logger = logging.getLogger('send_li_message_director')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from janium_functions.send_li_message.send_li_message_director.db_model import *
    from janium_functions.send_li_message.send_li_message_function import send_li_message_function
    logger = logging.getLogger('send_li_message_director')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)

def main(event, context):
    session = Session()
    topic_path = publisher.topic_path(PROJECT_ID, 'janium-send-li-message-topic')

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    clients = session.query(Client).filter(and_(
        Client.is_active == 1,
        Client.is_sending_li_messages == 1,
        Client.ulinc_config_id != Ulinc_config.unassigned_ulinc_config
    )).all()

    if now_date not in us_holidays:
        clients_list = []
        for client in clients:
            logger.debug(client.full_name)
            message_json = json.dumps(
                {"data": {"client_id": client.client_id}}
            )
            message_bytes = message_json.encode('utf-8')

            ## Publish message to send-li-message-topic ###
            try:
                if not os.getenv('LOCAL_DEV'): ### Trigger send_li_message_function main ###
                    publish_future = publisher.publish(topic_path, data=message_bytes)
                    publish_future.result()
                else: ### Trigger send_li_message_function main locally ###
                    payload = {"client_id": client.client_id}
                    payload = json.dumps(payload)
                    payload = base64.b64encode(str(payload).encode("utf-8"))
                    send_li_message_function.main({"data": payload}, 1)
                
                clients_list.append({"client_id": client.client_id, "client_full_name": client.full_name})
            except Exception as err:
                logger.error(str(err))
        logger.info('Messages to janium-send-li-message-topic published for clients {}'.format(clients_list))

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
