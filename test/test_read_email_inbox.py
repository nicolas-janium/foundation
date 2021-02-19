import base64
import json
from datetime import datetime, timedelta
import sys
import os
import subprocess

import mock

from db.model import *
from db import model_setup
from janium_functions.read_email_inbox.read_email_inbox_function import read_email_inbox_function


def test_get_email_sends_contacts():
    model_setup.main()
    session = Session()

    client = session.query(Client).filter(Client.client_id == '67e736f3-9f35-4bf0-992f-1e8a5afa261a').first()

    contacts = read_email_inbox_function.get_email_sends_contacts(client)
    assert len(contacts) == 1
