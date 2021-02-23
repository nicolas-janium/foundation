import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import mock

from db.model import *
from db import local_db_setup

from janium_functions.poll_webhook.poll_webhook_director import poll_webhook_director as director
from janium_functions.poll_webhook.poll_webhook_function import poll_webhook_function as function

mtn_time = datetime.utcnow() - timedelta(hours=7)

mock_context = mock.Mock()
mock_context.event_id = '617187464135194'
mock_context.timestamp = mtn_time


def test_poll_webhook_main():
    model_setup.main()

    payload = {"from": "schedule"}
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {"data": payload}

    return_list = director.main(event, mock_context)

    session = Session()

    contacts = session.query(Contact).all()

    assert len(contacts) == 38