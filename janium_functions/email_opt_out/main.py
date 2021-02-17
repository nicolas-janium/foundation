import os
from datetime import datetime, timedelta
from uuid import uuid4()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import *


def main(request):
    args = request.args
    opt_out_url = str(os.getenv('EMAIL_OPT_OUT_URL'))

    if args['landing'] == '1':
        redirect_url = opt_out_url + '?contactid={}&landing=0&contact_email={}'.format(args['contactid'], args['contact_email'])

        return r"""\
        <h1 style="text-align: center;">Manage Email Preferences</h1>
        <h4 style="text-align: center;">Email Address: {contact_email}</h4>
        <hr />
        <p style="text-align: center;">If you feel you have received this email on accident or wish to blacklist your email in our system, please click on this <a href="{redirect}">link</a>.</p>\
        """.replace(r"{contact_email}", args['contact_email']).replace(r"{redirect}", redirect_url)
    else:
        session = Session()

        new_action = Action(str(uuid4()), args['contactid'], 7, datetime.now() - timedelta(hours=7), None)
        session.add(new_action) # pylint: disable=no-member
        session.commit() # pylint: disable=no-member

        return r"""\
        <h1 style="text-align: center;">Manage Email Preferences</h1>
        <h4 style="text-align: center;">Email Address: {contact_email}</h4>
        <hr />
        <p style="text-align: center;">Your email has been blacklisted. You will not receive any more emails from us. Sorry for the inconvenience!</p>\
        """.replace(r"{contact_email}", args['contact_email'])


# if __name__ == '__main__':
#     with open('./functions/email_opt_out/landing_page.html', 'r') as f:
#         landing_page = f.read()
    
#     print(landing_page)
