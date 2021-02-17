import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import mock

from janium_functions.send_dte.send_dte_function.db_model import Session

from janium_functions.send_dte.send_dte_director import send_dte_director as director
from janium_functions.send_dte.send_dte_function import send_dte_function as function

mtn_time = datetime.utcnow() - timedelta(hours=7)

mock_context = mock.Mock()
mock_context.event_id = '617187464135194'
mock_context.timestamp = mtn_time

# def test_send_dte():
#     payload = {"from": "schedule"}
#     payload = json.dumps(payload)
#     payload = base64.b64encode(str(payload).encode("utf-8"))
#     event = {"data": payload}

#     return_value = director.main(event, mock_context)
#     assert 'nic@janium.io' == return_value

def test_get_new_connections():
    session = Session()
    nc = function.get_new_connections('67e736f3-9f35-4bf0-992f-1e8a5afa261a', session)
    assert nc[0][0] == 'Test1 Contact1' and len(nc) == 1

def test_get_new_messages():
    session = Session()
    nc = function.get_new_messages('67e736f3-9f35-4bf0-992f-1e8a5afa261a', session)
    assert len(nc) == 0

def test_get_new_voicemail_tasks():
    session = Session()
    nc = function.get_new_voicemail_tasks('67e736f3-9f35-4bf0-992f-1e8a5afa261a', session)
    assert len(nc) == 0