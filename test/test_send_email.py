import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import mock

from janium_functions.send_email.send_email_function.db_model import Session, Client, Janium_campaign

from janium_functions.send_email.send_email_director import send_email_director as director
from janium_functions.send_email.send_email_function import send_email_function as function

mtn_time = datetime.utcnow() - timedelta(hours=7)

mock_context = mock.Mock()
mock_context.event_id = '617187464135194'
mock_context.timestamp = mtn_time

# def test_send_email():
#     payload = {"from": "schedule"}
#     payload = json.dumps(payload)
#     payload = base64.b64encode(str(payload).encode("utf-8"))
#     event = {"data": payload}

#     assert 'nic@janium.io' == director.main(event, mock_context)

def test_get_email_targets():
    session = Session()
    client = session.query(Client).filter(Client.client_id == '67e736f3-9f35-4bf0-992f-1e8a5afa261a').first()
    janium_campaign = client.janium_campaigns.filter(Janium_campaign.is_messenger == False).first()
    is_sendgrid = True if client.email_config.is_sendgrid and client.email_config.sendgrid_sender_id else False

    email_targets_list = function.get_email_targets(client, janium_campaign, is_sendgrid)
    assert len(email_targets_list) == 4
