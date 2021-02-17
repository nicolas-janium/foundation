from datetime import datetime

import requests
from bs4 import BeautifulSoup as Soup


def get_ulinc_client_info(username, password):
    login_url = 'https://ulinc.co/login/?email={}&password={}&sign=1'.format(username, password)
    account_url = 'https://ulinc.co/accounts/'
    session = requests.Session()
    login = session.post(url=login_url)

    jar = requests.cookies.RequestsCookieJar()
    ulinc_cookie = {}

    for cookie in login.history[0].cookies:
        if cookie.name == 'PHPSESSID':
            continue
        elif cookie.name == 'usr':
            ulinc_cookie['usr'] = cookie.value
            ulinc_cookie['expires'] = datetime.fromtimestamp(cookie.expires).strftime(r'%Y-%m-%d %H:%M:%S')
            jar.set('usr', cookie.value)
        elif cookie.name == 'pwd':
            ulinc_cookie['pwd'] = cookie.value
            jar.set('pwd', cookie.value)

    account_page = session.get(url=account_url, cookies=jar)

    id_index = account_page.text.find('acc_')
    user_id1 = account_page.text[id_index + 4:id_index + 11]

    soup = Soup(account_page.text, 'html.parser')
    for link in soup.find_all('a'):
        if link.text == 'Settings':
            account_settings_link = link['href']
            user_id2 = account_settings_link.split('/')[3]

    if user_id1 == user_id2:
        ulinc_id = user_id1

    settings_url = 'https://ulinc.co/{}/?do=accounts&act=settings'.format(ulinc_id)
    settings_page = session.get(url=settings_url, cookies=jar)

    webhooks = {}
    soup = Soup(settings_page.text, 'html.parser')
    for i, element in enumerate(soup.find_all('input')[-3:]):
        if i == 0:
            webhooks['new_connection'] = element['value']
        elif i == 1:
            webhooks['new_message'] = element['value']
        elif i == 2:
            webhooks['send_message'] = element['value']

    return_data = {
        "ulinc_id": ulinc_id,
        "user_cookie": ulinc_cookie,
        "webhooks": webhooks
    }
    return return_data

def main(request):
    request_json = request.get_json()
    if request_json['from'] == 'retool':
        return get_ulinc_client_info(request_json['ulinc_username'], request_json['ulinc_password'])
