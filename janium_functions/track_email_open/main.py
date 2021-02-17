from sal_db import Activity, get_db_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def main(request):
    # print('request: {}'.format(request))
    args = request.args
    print('request args messageid {}'.format(args['messageid']))
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    existing_open = session.query(Activity).filter(Activity.email_message_id == args['messageid']).filter(Activity.action_code == 5).first()

    if existing_open:
        print('The open has already been recorded. Skipping insert query')
        return ''

    activity = Activity(args['contactid'], datetime.now(), 5, None, args['messageid'], False, None)
    session.add(activity)
    session.commit()
    print('Email opened and tracked')
    return ''
