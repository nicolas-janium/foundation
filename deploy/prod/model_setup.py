from deploy.staging.model import *
from deploy.staging.model_types import *
import json
from uuid import uuid4
import os
from datetime import datetime, timedelta
from workdays import networkdays, workday

mtn_time = datetime.utcnow() - timedelta(hours=7)

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

def main():
    session = Session()

    # Insert defaults and types
    insert_types(session)

    # Add unassigned records
    add_unassigned_records(session)

    # Add janium records
    add_janium_records(session)


if __name__ == '__main__':
    main()
