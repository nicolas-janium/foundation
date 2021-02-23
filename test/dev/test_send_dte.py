import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import mock
import pytest

from db.model import *
from db import local_db_setup

from janium_functions.send_dte.send_dte_director import send_dte_director as director
from janium_functions.send_dte.send_dte_function import send_dte_function as function

mtn_time = datetime.utcnow() - timedelta(hours=7)

mock_context = mock.Mock()
mock_context.event_id = '617187464135194'
mock_context.timestamp = mtn_time


def test_get_new_connections():
    model_setup.main()
    session = Session()
    nc = function.get_new_connections('67e736f3-9f35-4bf0-992f-1e8a5afa261a', session)
    assert nc[0][0] == 'Test 1 Contact 1' and len(nc) == 1

def test_get_new_messages():
    model_setup.main()
    session = Session()
    nc = function.get_new_messages('67e736f3-9f35-4bf0-992f-1e8a5afa261a', session)
    assert len(nc) == 2

def test_get_new_voicemail_tasks():
    model_setup.main()
    session = Session()
    nc = function.get_new_voicemail_tasks('67e736f3-9f35-4bf0-992f-1e8a5afa261a', 25, session)
    assert len(nc) == 1

def test_send_dte():
    model_setup.main()
    payload = {"from": "schedule"}
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {"data": payload}

    assert 'nic@janium.io' == director.main(event, mock_context)