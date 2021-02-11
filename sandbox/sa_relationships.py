from sandbox_db_model import *

session = Session()

contact = session.query(Contact).filter(Contact.contact_id == '06d1a22e-9aa3-44e6-bc13-6830c81fece0').first()

actions = contact.actions
connection_action = [action for action in actions if action.action_type_id == 10]
print(len(connection_action))