campaign_step_type_dict = {
    "li_message": {
        "id": 1,
        "description": "This is the LI message campaign step"
    },
    "email": {
        "id": 2,
        "description": "This is the email message campaign step"
    },
    "text_message": {
        "id": 3,
        "description": "This is the text message campaign step"
    }
}

action_type_dict = {
    "li_new_connection": {
        "id": 1,
        "description": "The contact onnection request accepted. Originates in Ulinc"
    },
    "li_new_message": {
        "id": 2,
        "description": "The client received a new li message from this contact. Originates in Ulinc"
    },
    "li_send_message": {
        "id": 3,
        "description": "The client sent a li message to this contact. Originates in Janium through Ulinc"
    },
    "send_email": {
        "id": 4,
        "description": "The client sent an email to this contact. Originates in Janium."
    },
    "contact_open_email": {
        "id": 5,
        "description": "The contact opened a previously sent email. "
    },
    "new_email": {
        "id": 6,
        "description": "The contact sent an email to the client."
    },
    "email_blacklist": {
        "id": 7,
        "description": "The contact unsubscribed from a sent email from the client."
    },
    "dte_profile_visit_nc": {
        "id": 8,
        "description": "The client visited the LI profile of this contact. Originates in DTE New Connection section"
    },
    "dte_profile_visit_nm": {
        "id": 9,
        "description": "The client visited the LI profile of this contact. Originates in DTE New Message section"
    },
    "dte_profile_visit_vm": {
        "id": 10,
        "description": "The client visited the LI profile of this contact. Originates in DTE Voicemail section"
    },
    "marked_to_no_interest": {
        "id": 11,
        "description": "The client DQ'd this contact. Originates in DTE"
    },
    "arbitrary_response": {
        "id": 12,
        "description": "The contact responded with an arbitrary response and further campaign steps should continue."
    }
}

credentails_type_dict = {
    "email_app": {
        "id": 1,
        "description": "Credentials for email app username and password in order to send emails and read inboxes"
    },
    "sendgrid": {
        "id": 2,
        "description": "Sendgrid is a third party email deliverer service"
    },
    "ulinc": {
        "id": 3,
        "description": "Ulinc login creds"
    }
}

webhook_response_type_dict = {
    "ulinc_new_connection": {
        "id": 1,
        "description": "New connection webhook from ulinc"
    },
    "ulinc_new_message": {
        "id": 2,
        "description": "New message webhook from ulinc"
    },
    "ulinc_send_message": {
        "id": 3,
        "description": "Send message webhook from ulinc"
    }
}

cookie_type_dict = {
    "ulinc_cookie": {
        "id": 1,
        "description": "Cookie type for Ulinc"
    }
}