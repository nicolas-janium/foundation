import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import requests
import urllib3
import mock

from db.model import *
from db import local_db_setup

from janium_functions.send_li_message.send_li_message_director import send_li_message_director as director
from janium_functions.send_li_message.send_li_message_function import send_li_message_function as function

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mtn_time = datetime.utcnow() - timedelta(hours=7)

mock_context = mock.Mock()
mock_context.event_id = '617187464135194'
mock_context.timestamp = mtn_time

def test_get_li_message_targets():
    session = Session()
    model_setup.main()

    client = session.query(Client).filter(Client.client_id == '67e736f3-9f35-4bf0-992f-1e8a5afa261a').first()
    janium_campaign = client.janium_campaigns.filter(Janium_campaign.is_messenger == False).first()

    li_message_targets_list = function.get_li_message_targets(client, janium_campaign)
    assert len(li_message_targets_list) == 4

# def test_send_li_message():
#     session = Session()
#     model_setup.main()

#     payload = {"from": "schedule"}
#     payload = json.dumps(payload)
#     payload = base64.b64encode(str(payload).encode("utf-8"))
#     event = {"data": payload}

#     return_list = director.main(event, mock_context)

#     assert len(return_list) == 4 
