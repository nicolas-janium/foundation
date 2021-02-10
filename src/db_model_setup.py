from db_model import (Action_type, Campaign_step_type, Client, Client_group,
                      Client_group_manager, Cookie_type, Credentials_type, Dte,
                      Dte_sender, Email_server, Session, Webhook_response,
                      Webhook_response_type)
from db_model_types import *

# Insert campaign step types
session = Session()

# Insert Campaign Step Types
for key in campaign_step_type_dict:
    if not session.query(Campaign_step_type).filter(Campaign_step_type.campaign_step_type_id == campaign_step_type_dict[key]['id']).first():
        campaign_step_type = Campaign_step_type(campaign_step_type_dict[key]['id'], key, campaign_step_type_dict[key]['description'])
        session.add(campaign_step_type)

# Insert Action Types
for key in action_type_dict:
    if not session.query(Action_type).filter(Action_type.action_type_id == action_type_dict[key]['id']).first():
        action_type = Action_type(action_type_dict[key]['id'], key, action_type_dict[key]['description'])
        session.add(action_type)

# Insert Credentials Types
for key in credentails_type_dict:
    if not session.query(Credentials_type).filter(Credentials_type.credentials_type_id == credentails_type_dict[key]['id']).first():
        credentials_type = Credentials_type(credentails_type_dict[key]['id'], key, credentails_type_dict[key]['description'])
        session.add(credentials_type)

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

session.commit()


# Insert Dummy email server
if not session.query(Email_server).filter(Email_server.email_server_id == Email_server.dummy_email_server_id).first():
    dummy_email_server = Email_server(Email_server.dummy_email_server_id, 'Dummy Email Server', 'dummy.smtp', 999, 999, 'dummy.imap', 999)
    session.add(dummy_email_server)

# Insert Dummy Dte
if not session.query(Dte).filter(Dte.dte_id == Dte.dummy_dte_id).first():
    dummy_dte = Dte(Dte.dummy_dte_id, 'Dummy Dte', 'Dummy Dte Description', 'Dummy Subject', 'Dummy Body')
    session.add(dummy_dte)

# Insert Dummy Dte Sender
if not session.query(Dte_sender).filter(Dte_sender.dte_sender_id == Dte_sender.dummy_dte_sender_id).first():
    dummy_dte_sender = Dte_sender(Dte_sender.dummy_dte_sender_id, 'Dummy', 'Dte Sender')
    session.add(dummy_dte_sender)

# Insert Dummy Client Group Manager
if not session.query(Client_group_manager).filter(Client_group_manager.client_group_manager_id == Client_group_manager.dummy_client_group_manager_id).first():
    dummy_client_group_manager = Client_group_manager(Client_group_manager.dummy_client_group_manager_id, 'Dummy', 'Dumb')
    session.add(dummy_client_group_manager)

# Insert Dummy Client Group
if not session.query(Client_group).filter(Client_group.client_group_id == Client_group.dummy_client_group_id).first():
    dummy_client_group = Client_group(
        Client_group.dummy_client_group_id,
        Client_group_manager.dummy_client_group_manager_id,
        Dte.dummy_dte_id, Dte_sender.dummy_dte_sender_id,
        'Dummy Client Group',
        'Dummy Description',
        False
    )
    session.add(dummy_client_group)

# Insert Dummy Client
if not session.query(Client).filter(Client.client_id == Client.dummy_client_id).first():
    dummy_client = Client(
        Client.dummy_client_id,
        Client_group.dummy_client_group_id,
        False, False, False, False, 'Dummy', 'Client',
        None, None, None, 'dummy@gmail.com', None, None,
        None, None, None, None
    )
    session.add(dummy_client)

# Insert Dummy Webhook Response
if not session.query(Webhook_response).filter(Webhook_response.webhook_response_id == Webhook_response.dummy_webhook_response_id).first():
    dummy_webhook_response = Webhook_response(
        Webhook_response.dummy_webhook_response_id,
        Client.dummy_client_id,
        r"{'data': 'empty'}",
        1
    )
    session.add(dummy_webhook_response)

session.commit()
