from db_model import *
from db_model_types import *
import json
from uuid import uuid4
import os
from datetime import datetime

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

def add_testing_records(session):
    ## Credentials ##
    ulinc_credentials = Credentials(
        str(uuid4()),
        'jhawkes20@gmail.com',
        'JA12345!'
    )
    email_app_credentials = Credentials(
        str(uuid4()),
        'jason@thecxo100.com',
        'fqgusrumwptpbpae'
    )
    session.add(ulinc_credentials)
    session.add(email_app_credentials)

    ## Cookie ##
    ulinc_cookie = Cookie(
        str(uuid4()),
        1,
        {
            "usr": "48527",
            "pwd": "93fd3060131f8f9e8410775809f0a231",
            "expires": "2021-12-05 08:00:21"
        }
    )
    session.add(ulinc_cookie)

    ## Ulinc Config ##
    ulinc_config = Ulinc_config(
        str(uuid4()),
        ulinc_credentials.credentials_id,
        ulinc_cookie.cookie_id,
        '5676186',
        'https://ulinc.co/zap/04504f40b9401feb443197523bafa1b9',
        'https://ulinc.co/zap/40cb47aaf09c8f1447415a564a12278e',
        'https://ulinc.co/zap/44cde3d9c69af6db363371e3c21286e3'
    )
    session.add(ulinc_config)

    # Email Config
    email_config = Email_config(
        str(uuid4()),
        email_app_credentials.credentials_id,
        email_server_dict['yahoo_small_business']['id'],
        False, None
    )
    session.add(email_config)

    ## Dte and Dte Sender ##
    dte = Dte(
        str(uuid4()),
        'Test DTE Name',
        'Test DTE Description',
        'Test DTE Subject',
        'Test DTE Body'
    )
    dte_sender = Dte_sender(
        str(uuid4()),
        email_config.email_config_id,
        'Jason',
        'Hawkes'
    )
    session.add(dte)
    session.add(dte_sender)

    # Client Group Manager
    client_group_manager = Client_group_manager(
        str(uuid4()),
        'Default Client',
        'Group Manager'
    )
    session.add(client_group_manager)

    # Client Group
    client_group = Client_group(
        str(uuid4()),
        client_group_manager.client_group_manager_id,
        dte.dte_id,
        dte_sender.dte_sender_id,
        'Test Client Group Name',
        'Test Client Group Description',
        True
    )
    session.add(client_group)

    ## Client ##
    client = Client(
        # str(uuid4()),
        '8a52cdff-6722-4d26-9a6a-55fe952bbef1',
        client_group.client_group_id, 
        ulinc_config.ulinc_config_id,
        email_config.email_config_id,
        False, False, False, False, False, 'Jonny', 'Karate',
        None, None, None, 'jonny.karate@gmail.com', None, None,
        None, None, None, None
    )
    session.add(client)
    session.commit()

    ## Campaign ##
    janium_connector_campaign = Janium_campaign(
        str(uuid4()),
        client.client_id,
        email_config.email_config_id,
        'Test Janium Connector Campaign Name',
        'Test Janium Connector Campaign Description',
        True,
        False
    )
    janium_messenger_campaign = Janium_campaign(
        str(uuid4()),
        client.client_id,
        email_config.email_config_id,
        'Test Janium Messenger Campaign Name',
        'Test Janium Messenger Campaign Description',
        True,
        True
    )
    unnassigned_janium_campaign = Janium_campaign(
        '9d6c1500-233f-42e2-9e02-725a22c831dc',
        client.client_id,
        email_config.email_config_id,
        'Unassigned Janium Campaign Value',
        None,
        False,
        False
    )
    ulinc_connector_campaign1 = Ulinc_campaign(
        str(uuid4()),
        client.client_id,
        janium_connector_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 1 Name',
        True,
        '101',
        False,
        None
    )
    ulinc_connector_campaign2 = Ulinc_campaign(
        str(uuid4()),
        client.client_id,
        janium_connector_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 2 Name',
        True,
        '102',
        False,
        None
    )
    ulinc_connector_campaign3 = Ulinc_campaign(
        str(uuid4()),
        client.client_id,
        janium_messenger_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 3 Name',
        True,
        '103',
        False,
        None
    )
    ulinc_connector_campaign4 = Ulinc_campaign(
        str(uuid4()),
        client.client_id,
        janium_messenger_campaign.janium_campaign_id,
        'Test Ulinc Connector Campaign 4 Name',
        True,
        '104',
        False,
        None
    )
    unnassigned_ulinc_campaign = Ulinc_campaign(
        'f98af084-3a30-4036-870d-4ad5859dbc4c',
        client.client_id,
        unnassigned_janium_campaign.janium_campaign_id,
        'Unnassigned Ulinc Campaign Name',
        True,
        '999',
        False,
        None
    )
    session.add(janium_connector_campaign)
    session.add(janium_messenger_campaign)
    session.add(unnassigned_janium_campaign)

    session.add(ulinc_connector_campaign1)
    session.add(ulinc_connector_campaign2)
    session.add(ulinc_connector_campaign3)
    session.add(ulinc_connector_campaign4)
    session.add(unnassigned_ulinc_campaign)
    ## Webhook Response ##
    webhook_response = Webhook_response(
        str(uuid4()),
        client.client_id,
        {
            "data": "Some Value"
        },
        1
    )
    session.add(webhook_response)

    ## Campaign Steps and contacts ##
    for i in range(1, 9):
        if i % 2 == 0:
            step_type = 'email'
        else:
            step_type = 'li_message'
        campaign_step = Janium_campaign_step(
            str(uuid4()),
            janium_connector_campaign.janium_campaign_id,
            campaign_step_type_dict[step_type]['id'],
            True,
            (i + 1) * 3,
            'Janium Campaign Step {} {} Body'.format(i, step_type),
            'Janium Campaign Step {} {} Subject'.format(i, step_type) if i % 2 == 0 else None,
        )
        session.add(campaign_step)

        # contact = Contact(
        #     str(uuid4()),
        #     client.client_id,
        #     janium_campaign.janium_campaign_id,
        #     ulinc_campaign.ulinc_campaign_id,
        #     webhook_response.webhook_response_id,
        #     '12345678',
        #     ulinc_campaign.ulinc_ulinc_campaign_id,
        #     'Test{}'.format(i),
        #     'Contact{}'.format(i),
        #     None, None, None, 'nic@janium.io', None, None, None, None, None
        # )
        # session.add(contact)

        # connection_action = Action(
        #     str(uuid4()),
        #     contact.contact_id,
        #     1,
        #     None,
        #     None
        # )
        # session.add(connection_action)

        # for j in range(1,i):
        #     action = Action(
        #         str(uuid4()),
        #         contact.contact_id,
        #         4 if j % 2 == 0 else 3,
        #         datetime.now(),
        #         'Message Body'
        #     )
        #     session.add(action)

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
    session = Session()

    # Insert defaults and types
    insert_types(session)

    # Reset db
    reset_db(session)

    # Add testing records
    add_testing_records(session)


if __name__ == '__main__':
    main()
