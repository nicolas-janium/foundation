from datetime import datetime
from uuid import uuid4

from flask import redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import Action, Session


def main(request):
    args = request.args
    profile_url = args['redirect_url']

    session = Session()

    new_action = Action(str(uuid4()), args['contactid'], datetime.now(), 8, None, None, False, None)
    session.add(new_action) # pylint: disable=no-member
    session.commit() # pylint: disable=no-member

    return redirect(profile_url)
