import base64
import json
from datetime import datetime
import logging
import sys
import os
import pytz

from google.cloud import pubsub_v1
from sqlalchemy import and_, or_

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('data_enrichment_director')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *
    from janium_functions.data_enrichment.data_enrichment_function import main as function

    logger = logging.getLogger('data_enrichment_director')
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
    topic_path = publisher.topic_path(PROJECT_ID, 'janium-data-enrichment-topic')

    session = get_session()

    accounts = session.query(Account).filter(and_(
        and_(Account.effective_start_date < datetime.utcnow(), Account.effective_end_date > datetime.utcnow()),
        and_(Account.data_enrichment_start_date < datetime.utcnow(), Account.data_enrichment_end_date > datetime.utcnow()),
    )).all()

    accounts_list = []
    for account in accounts:
        print(account.account_id)
        message_json = json.dumps(
            {"account_id": account.account_id}
        )
        message_bytes = message_json.encode('utf-8')

        ## Publish message to send-dte-function ###
        try:
            if not os.getenv('LOCAL_DEV'):
                publish_future = publisher.publish(topic_path, data=message_bytes)
                publish_future.result()
            else:
                payload = {"account_id": account.account_id}
                payload = json.dumps(payload)
                payload = base64.b64encode(str(payload).encode("utf-8"))
                return function.main({"data": payload}, 1)
            accounts_list.append({"account_id": account.account_id})
            # return 'OKKKK'
        except Exception as err:
            logger.error(str(err))
    logger.info('Messages to janium-poll-ulinc-csv-topic published for accounts {}'.format(accounts_list))

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
