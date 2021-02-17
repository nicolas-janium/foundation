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
        "description": "The contact connection request accepted. Originates in Ulinc"
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
    },
    "ulinc_origin_messenger_message": {
        "id": 13,
        "description": "This is the origin message for Ulinc Messenger Campaigns"
    },
    "li_new_connection_backdated": {
        "id": 14,
        "description": "The contact connection request accepted if contact is backdated into a janium campaign"
    },
    "email_bounce": {
        "id": 15,
        "description": "The contact was sent an email that bounced. Originates from Sendgrid"
    },
    "tib_new_vendor": {
        "id": 16,
        "description": "When a new vendor registers on TIB"
    },
    "tib_vendor_retire": {
        "id": 17,
        "description": "When a new vendor submits a meeting request"
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

email_server_dict = {
    "gmail": {
        "id": "f9cf23f6-231c-4210-90f3-7749873909ad",
        "smtp_address": "smtp.gmail.com",
        "smtp_tls_port": 587,
        "smtp_ssl_port": 465,
        "imap_address": "imap.gmail.com",
        "imap_ssl_port": 993
    },
    "office_365": {
        "id": "9e29868d-65dc-4d12-9bfb-9ee38f639773",
        "smtp_address": "smtp.office365.com",
        "smtp_tls_port": 587,
        "smtp_ssl_port": 465,
        "imap_address": "outlook.office365.com",
        "imap_ssl_port": 993
    },
    "yahoo_small_business": {
        "id": "5fbb236e-16e6-4a98-94fe-ff11f2b222b3",
        "smtp_address": "smtp.bizmail.yahoo.com",
        "smtp_tls_port": 587,
        "smtp_ssl_port": 465,
        "imap_address": "imap.mail.yahoo.com",
        "imap_ssl_port": 993
    }
}