# from deploy.staging.model import *
# from deploy.staging.model_types import *
import json
from uuid import uuid4
import os
from datetime import datetime, timedelta
from workdays import networkdays, workday
from db.model import *
from db.model_types import *

mtn_time = datetime.utcnow() - timedelta(hours=7)

jonny_client_id = '67e736f3-9f35-4bf0-992f-1e8a5afa261a'

jonny_ulinc_config_id = '50978461-c815-406d-b569-4054f142e86a'
jonny_ulinc_cookie_id = '05a68dea-ea9a-424e-ad18-cdf38bf0069e'
jonny_ulinc_credentials_id = 'bd3ffcd7-deaf-4a7a-9510-ccfe6025829c'

jonny_email_config_id = 'd9379706-1494-4e74-83ab-8aa3d778a7a7'
jonny_email_app_credentials_id = '26fe2440-35b0-49de-9dc7-931c2ad71a39'

jonny_webhook_response_id = '9aacedb7-c03f-4ccf-9e03-950e5039ec6d'

def insert_types(session):
    # Insert Janium_campaign Step Types
    for key in campaign_step_type_dict:
        if not session.query(Janium_campaign_step_type).filter(Janium_campaign_step_type.janium_campaign_step_type_id == campaign_step_type_dict[key]['id']).first():
            janium_campaign_step_type = Janium_campaign_step_type(campaign_step_type_dict[key]['id'], key, campaign_step_type_dict[key]['description'])
            session.add(janium_campaign_step_type)

    # Insert Action Types
    for key in action_type_dict:
        if not session.query(Action_type).filter(Action_type.action_type_id == action_type_dict[key]['id']).first():
            action_type = Action_type(action_type_dict[key]['id'], key, action_type_dict[key]['description'])
            session.add(action_type)

    # Insert Webhook Response Types
    for key in webhook_response_type_dict:
        if not session.query(Webhook_response_type).filter(Webhook_response_type.webhook_response_type_id == webhook_response_type_dict[key]['id']).first():
            webhook_response_type = Webhook_response_type(webhook_response_type_dict[key]['id'], key, webhook_response_type_dict[key]['description'])
            session.add(webhook_response_type)

    # Insert Cookie Types
    for key in cookie_type_dict:
        if not session.query(Cookie_type).filter(Cookie_type.cookie_type_id == cookie_type_dict[key]['id']).first():
            cookie_type = Cookie_type(cookie_type_dict[key]['id'], key, cookie_type_dict[key]['description'])
            session.add(cookie_type)

    for key in email_server_dict:
        if not session.query(Email_server).filter(Email_server.email_server_id == email_server_dict[key]['id']).first():
            email_server = Email_server(
                email_server_dict[key]['id'],
                key,
                email_server_dict[key]['smtp_address'],
                email_server_dict[key]['smtp_tls_port'],
                email_server_dict[key]['smtp_ssl_port'],
                email_server_dict[key]['imap_address'],
                email_server_dict[key]['imap_ssl_port']
            )
            session.add(email_server)

    session.commit()

def add_unassigned_records(session):
    unassigned_ulinc_credentials = Credentials(str(uuid4()), '', '')
    session.add(unassigned_ulinc_credentials)

    unassigned_email_app_credentials = Credentials(str(uuid4()), '', '')
    session.add(unassigned_email_app_credentials)

    unassigned_ulinc_cookie = Cookie(Cookie.unassigned_cookie_id, 1, {'key': 'Some value'})
    session.add(unassigned_ulinc_cookie)

    unassigned_ulinc_config = Ulinc_config(Ulinc_config.unassigned_ulinc_config_id, unassigned_ulinc_credentials.credentials_id, unassigned_ulinc_cookie.cookie_id, '', '', '', '')
    session.add(unassigned_ulinc_config)

    unassigned_email_config = Email_config(Email_config.unassigned_email_config_id, unassigned_email_app_credentials.credentials_id, 'f9cf23f6-231c-4210-90f3-7749873909ad', False, None)
    session.add(unassigned_email_config)

    unassigned_dte = Dte(str(uuid4()), 'Unnassigned DTE Name', 'Description', 'Subject', 'Body')
    session.add(unassigned_dte)

    unassigned_dte_sender = Dte_sender(str(uuid4()), unassigned_email_config.email_config_id, 'Unassigned', 'DTE Sender')
    session.add(unassigned_dte_sender)

    unassigned_client_group_manager = Client_group_manager(str(uuid4()), 'Unassigned', 'Client Group Manager')
    session.add(unassigned_client_group_manager)

    unassigned_client_group = Client_group(
        str(uuid4()),
        unassigned_client_group_manager.client_group_manager_id,
        unassigned_dte.dte_id,
        unassigned_dte_sender.dte_sender_id,
        'Unassigned Client Group',
        'Description',
        False
    )
    session.add(unassigned_client_group)

    unassigned_client = Client(
        str(uuid4()), unassigned_client_group.client_group_id, unassigned_ulinc_config.ulinc_config_id, unassigned_email_config.email_config_id,
        False, False, False, False, False, 'Unassigned', 'Client', None, None, None, 'unassigned@gmail.com', None, None, None, None, None, None, None, False
    )
    session.add(unassigned_client)

    unassigned_janium_campaign = Janium_campaign(
        Janium_campaign.unassigned_janium_campaign_id,
        unassigned_client.client_id,
        unassigned_email_config.email_config_id,
        'Unassigned Janium Campaign Name',
        'Description', False, False
    )
    session.add(unassigned_janium_campaign)

    unassigned_ulinc_campaign = Ulinc_campaign(
        Ulinc_campaign.unassigned_ulinc_campaign_id,
        unassigned_client.client_id,
        unassigned_janium_campaign.janium_campaign_id,
        'Unassigned Ulinc Campaign Name',
        False, '999', False, None
    )
    session.add(unassigned_ulinc_campaign)
    session.commit()

def add_janium_records(session):
    janium_email_app_credentials = Credentials(Credentials.janium_email_app_credentials_id, os.getenv('NIC_EMAIL_APP_USERNAME'), os.getenv('NIC_EMAIL_APP_PASSWORD'))
    session.add(janium_email_app_credentials)

    janium_email_config = Email_config(
        Email_config.janium_email_config_id,
        janium_email_app_credentials.credentials_id,
        email_server_dict['gmail']['id'],
        False,
        None
    )
    session.add(janium_email_config)

    janium_dte = Dte(
        Dte.janium_dte_id,
        'Main DTE for Janium Users',
        'This is the main DTE for all users that are independent or belong to Janium',
        'Janium Daily Task Test Email Subject',
        open("dte_templates/janium_dte.html", "r").read()
    )
    janium_dte_sender = Dte_sender(
        Dte_sender.janium_dte_sender_id,
        janium_email_config.email_config_id,
        'Nicolas',
        'Arnold'
    )
    session.add(janium_dte)
    session.add(janium_dte_sender)

    # Janium Client Group Manager
    janium_client_group_manager = Client_group_manager(
        Client_group_manager.janium_client_group_manager_id,
        'Nicolas',
        'Arnold'
    )
    session.add(janium_client_group_manager)

    # Janium Client Group
    janium_client_group = Client_group(
        Client_group.janium_client_group_id,
        janium_client_group_manager.client_group_manager_id,
        janium_dte.dte_id,
        janium_dte_sender.dte_sender_id,
        'Janium Client Group',
        'This is the main Janium Group. Any independent user will be assigned to this group',
        True
    )
    session.add(janium_client_group)
    session.commit()


def add_jonny_records(session):
    ## Credentials ##
    jonny_ulinc_credentials = Credentials(jonny_ulinc_credentials_id, 'jhawkes20@gmail.com', 'JA12345!')
    jonny_email_app_credentials = Credentials(jonny_email_app_credentials_id, os.getenv('JASON_EMAIL_APP_USERNAME'), os.getenv('JASON_EMAIL_APP_PASSWORD'))
    session.add(jonny_ulinc_credentials)
    session.add(jonny_email_app_credentials)

    ## Cookie ##
    jonny_ulinc_cookie = Cookie(
        jonny_ulinc_cookie_id,
        1,
        {
            "usr": "48527",
            "pwd": "93fd3060131f8f9e8410775809f0a231",
            "expires": "2021-12-05 08:00:21"
        }
    )
    session.add(jonny_ulinc_cookie)

    ## Ulinc Config ##
    jonny_ulinc_config = Ulinc_config(
        jonny_ulinc_config_id,
        jonny_ulinc_credentials.credentials_id,
        jonny_ulinc_cookie.cookie_id,
        '5676186',
        'https://ulinc.co/zap/04504f40b9401feb443197523bafa1b9',
        'https://ulinc.co/zap/40cb47aaf09c8f1447415a564a12278e',
        'https://ulinc.co/zap/44cde3d9c69af6db363371e3c21286e3'
    )
    session.add(jonny_ulinc_config)

    # Email Config
    jonny_email_config = Email_config(
        str(uuid4()),
        jonny_email_app_credentials.credentials_id,
        email_server_dict['yahoo_small_business']['id'],
        False, None
    )
    session.add(jonny_email_config)

    ## Client ##
    jonny_client = Client(
        jonny_client_id,
        Client_group.janium_client_group_id, 
        jonny_ulinc_config.ulinc_config_id,
        jonny_email_config.email_config_id,
        True, True, True, True, False, 'Jonny', 'Karate',
        None, None, None, 'nic@janium.io', None, None,
        None, None, None, None, 25, False
    )
    session.add(jonny_client)
    session.commit()

    ## Campaign ##
    janium_connector_campaign = Janium_campaign(
        str(uuid4()),
        jonny_client.client_id,
        jonny_email_config.email_config_id,
        'Test Janium Connector Campaign Name',
        'Test Janium Connector Campaign Description',
        True,
        False
    )
    janium_messenger_campaign = Janium_campaign(
        str(uuid4()),
        jonny_client.client_id,
        jonny_email_config.email_config_id,
        'Test Janium Messenger Campaign Name',
        'Test Janium Messenger Campaign Description',
        True,
        True
    )

    ulinc_connector_campaign1 = Ulinc_campaign(
        str(uuid4()),
        jonny_client.client_id,
        janium_connector_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 1 Name',
        True,
        '101',
        False,
        None
    )
    ulinc_connector_campaign2 = Ulinc_campaign(
        str(uuid4()),
        jonny_client.client_id,
        janium_connector_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 2 Name',
        True,
        '102',
        False,
        None
    )
    ulinc_connector_campaign3 = Ulinc_campaign(
        str(uuid4()),
        jonny_client.client_id,
        janium_messenger_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 3 Name',
        True,
        '103',
        False,
        None
    )
    ulinc_connector_campaign4 = Ulinc_campaign(
        str(uuid4()),
        jonny_client.client_id,
        janium_messenger_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 4 Name',
        True,
        '104',
        False,
        None
    )
    session.add(janium_connector_campaign)
    session.add(janium_messenger_campaign)

    session.add(ulinc_connector_campaign1)
    session.add(ulinc_connector_campaign2)
    session.add(ulinc_connector_campaign3)
    session.add(ulinc_connector_campaign4)

    ## Webhook Response ##
    jonny_webhook_response = Webhook_response(
        str(uuid4()),
        jonny_client.client_id,
        {
            "data": "Some Value"
        },
        1
    )
    session.add(jonny_webhook_response)

    ## Campaign Steps and contacts ##
    for i in range(1, 14):
        if i % 2 == 0:
            step_type = 'email'
        else:
            step_type = 'li_message'
        if i < 9:
            campaign_step = Janium_campaign_step(
                str(uuid4()),
                janium_connector_campaign.janium_campaign_id,
                campaign_step_type_dict[step_type]['id'],
                True,
                i * 3,
                'Janium Campaign Test 123 Step {} {} Body'.format(i, step_type),
                'Janium Campaign Test 123 Step {} {} Subject'.format(i, step_type) if i % 2 == 0 else None,
            )
            session.add(campaign_step)

        contact = Contact(
            str(uuid4()),
            jonny_client.client_id,
            janium_connector_campaign.janium_campaign_id,
            ulinc_connector_campaign1.ulinc_campaign_id,
            jonny_webhook_response.webhook_response_id,
            '56761861868',
            ulinc_connector_campaign1.ulinc_ulinc_campaign_id,
            'Test {}'.format(i),
            'Contact {}'.format(i),
            None, None, None, 'nic@janium.io', None, None, '12083133432', None, None, None
        )
        session.add(contact)

        connection_action = Action(
            str(uuid4()),
            contact.contact_id,
            1,
            workday(mtn_time, -25) if i == 11 else workday(mtn_time, -40) if i == 12 else workday(mtn_time, (-3 * i) + 1),
            None
        )
        session.add(connection_action)

        if i in [9,10]:
            message_action = Action(
                str(uuid4()),
                contact.contact_id,
                2 if i == 9 else 6,
                mtn_time,
                None
            )
            session.add(message_action)
        
        if i == 13:
            send_message_action = Action(
                str(uuid4()),
                contact.contact_id,
                4,
                mtn_time,
                None
            )
            session.add(send_message_action)

        # for j in range(1,i):
        #     action = Action(
        #         str(uuid4()),
        #         contact.contact_id,
        #         4 if j % 2 == 0 else 3,
        #         datetime.now(),
        #         'Message Body'
        #     )
        #     session.add(action)
        #     if i == 7 and j == 6:
        #         new_message_action = Action(str(uuid4()), contact.contact_id, 2, datetime.now(), None)
        #         session.add(new_message_action)
        #     elif i == 8 and j ==7:
        #         new_message_action = Action(str(uuid4()), contact.contact_id, 6, datetime.now(), None)
        #         session.add(new_message_action)


    session.commit()

def reset_db(session):
    session.query(Action).delete(synchronize_session='fetch')
    session.query(Contact).delete(synchronize_session='fetch')
    session.query(Webhook_response).delete(synchronize_session='fetch')

    session.query(Ulinc_campaign).delete(synchronize_session='fetch')
    session.query(Janium_campaign_step).delete(synchronize_session='fetch')
    session.query(Janium_campaign).delete(synchronize_session='fetch')
    
    
    session.query(Client).delete(synchronize_session='fetch')
    session.query(Client_group).delete(synchronize_session='fetch')
    session.query(Client_group_manager).delete(synchronize_session='fetch')

    session.query(Dte_sender).delete(synchronize_session='fetch')
    session.query(Dte).delete(synchronize_session='fetch')

    session.query(Email_config).delete(synchronize_session='fetch')
    session.query(Ulinc_config).delete(synchronize_session='fetch')
    session.query(Credentials).delete(synchronize_session='fetch')
    session.query(Cookie).delete(synchronize_session='fetch')
    
    session.commit()

def main():
    session = get_session(is_remote=True, environment='staging')

    # Insert defaults and types
    insert_types(session)

    # Reset db
    reset_db(session)

    # Add unassigned records
    add_unassigned_records(session)

    # Add janium records
    add_janium_records(session)

    # Add jonny records
    add_jonny_records(session)


if __name__ == '__main__':
    main()
