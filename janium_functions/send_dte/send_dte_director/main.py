import base64
import json
from datetime import datetime
import logging
import sys
import os

import holidays
from google.cloud import pubsub_v1
from sqlalchemy import and_, or_

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('send_dte_director')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *
    from janium_functions.send_dte.send_dte_function import main as function

    logger = logging.getLogger('send_dte_director')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


def main(event, context):
    # Instantiates a Pub/Sub client
    publisher = pubsub_v1.PublisherClient()
    PROJECT_ID = os.getenv('PROJECT_ID')
    topic_path = publisher.topic_path(PROJECT_ID, 'janium-send-dte-topic')

    session = Session()

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    clients = session.query(Client).filter(and_(Client.is_active == 1, Client.is_dte == 1)).all()

    if now_date not in us_holidays:
        clients_list = []
        for client in clients:
            message_json = json.dumps(
                {"data": {"client_id": client.client_id}}
            )
            message_bytes = message_json.encode('utf-8')

            ### Publish message to send-dte-function ###
            try:
                if not os.getenv('LOCAL_DEV'):
                    publish_future = publisher.publish(topic_path, data=message_bytes)
                    publish_future.result()
                else:
                    payload = {"client_id": client.client_id}
                    payload = json.dumps(payload)
                    payload = base64.b64encode(str(payload).encode("utf-8"))
                    return function.main({"data": payload}, 1)
                clients_list.append({"client_id": client.client_id, "client_full_name": client.full_name})
                # return 'OKKKK'
            except Exception as err:
                logger.error(str(err))
        logger.info('Messages to janium-send-dte-topic published for clients {}'.format(clients_list))

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
