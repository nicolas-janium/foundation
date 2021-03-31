import os
from uuid import uuid4
from datetime import datetime, timedelta

from db.model import *

def main():
    session = get_session()

    # ulinc_creds = Credentials(str(uuid4()), 'jhawkes20@gmail.com', 'JA12345!', User.system_user_id)
    # email_app_creds = Credentials(str(uuid4()), 'jason@janium.io', 'hmwutkvduanykfvl', User.system_user_id)
    # session.add(ulinc_creds)
    # session.add(email_app_creds)

    # ulinc_cookie = Cookie(str(uuid4()), 1, {"usr": "48527", "pwd": "93fd3060131f8f9e8410775809f0a231"}, User.system_user_id)
    # session.add(ulinc_cookie)

    # email_config = Email_config(
    #     str(uuid4()),
    #     email_app_creds.credentials_id,
    #     '936dce84-b50f-4b72-824f-b01989b20500',
    #     1,
    #     '1324325',
    #     False,
    #     User.system_user_id,
    #     'Jason Hawkes',
    #     'jason@janium.io'
    # )
    # session.add(email_config)

    # jason_account = Account(
    #     str(uuid4()),
    #     Account_group.unassigned_account_group_id,
    #     email_config.email_config_id,
    #     True,
    #     True,
    #     False,
    #     datetime.utcnow(),
    #     datetime.utcnow() + timedelta(days=100000),
    #     datetime.utcnow(),
    #     datetime.utcnow() + timedelta(days=100000),
    #     'b233c2b0-d600-43f1-98e2-ec9cf8023d19',
    #     User.system_user_id,
    #     1
    # )
    # session.add(jason_account)

    # ulinc_config = Ulinc_config(
    #     str(uuid4()),
    #     jason_account.account_id,
    #     ulinc_creds.credentials_id,
    #     ulinc_cookie.cookie_id,
    #     '5676186',
    #     'https://ulinc.co/zap/04504f40b9401feb443197523bafa1b9',
    #     'https://ulinc.co/zap/40cb47aaf09c8f1447415a564a12278e',
    #     'https://ulinc.co/zap/44cde3d9c69af6db363371e3c21286e3',
    #     'jason@janium.io',
    #     True,
    #     User.system_user_id
    # )
    # session.add(ulinc_config)

    # jason_user = User(
    #     str(uuid4()),
    #     'Jason',
    #     'Hawkes',
    #     None,
    #     None,
    #     None,
    #     'jason@janium.io',
    #     'jason@janium.io',
    #     None,
    #     None,
    #     User.system_user_id
    # )
    # session.add(jason_user)

    # janium_campaign = Janium_campaign(
    #     str(uuid4()),
    #     jason_account.account_id,
    #     email_config.email_config_id,
    #     'Jason Hawkes Janium Campaign Name',
    #     None,
    #     False,
    #     False,
    #     datetime.strptime('9999-12-31 08:00:00', '%Y-%m-%d %H:%M:%S'),
    #     datetime.strptime('9999-12-31 15:00:00', '%Y-%m-%d %H:%M:%S'),
    #     User.system_user_id
    # )
    # session.add(janium_campaign)

    # ulinc_campaign = Ulinc_campaign(
    #     str(uuid4()),
    #     jason_account.account_id,
    #     ulinc_config.ulinc_config_id,
    #     janium_campaign.janium_campaign_id,
    #     'IT+ - 50-500 - CO',
    #     True,
    #     '13',
    #     False,
    #     None,
    #     User.system_user_id
    # )
    # session.add(ulinc_campaign)

    # session.commit()



if __name__ == '__main__':
    main()

