import time

import requests
from selenium.webdriver import ActionChains


login = 'realestateavatarex@gmail.com'
password = 'wivqEd-sexno6-rejvyv'


class AmoConnect:
    login = ''
    password = ''
    amo_hash = ''
    host = ''

    session = ''
    headers = ''
    chat_token = ''
    csrf_token = ''
    access_token = ''
    refresh_token = ''

    def __init__(self, user_login: str, user_password: str, host='', token=''):
        self.login = user_login
        self.password = user_password
        self.host = host
        self.amo_hash = token
        self.auth()

    def _create_session(self):
        self.session = requests.Session()
        response = self.session.get('https://www.amocrm.ru/')
        session_id = response.cookies.get('session_id')
        self.csrf_token = response.cookies.get('csrf_token')
        self.headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'session_id={session_id}; '
                      f'csrf_token={self.csrf_token};',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/112.0.0.0 Safari/537.36'
        }

    def _get_host(self):
        response = self.session.get('https://www.amocrm.ru/v3/accounts').json()
        host = response['_embedded']['items'][0]['domain']
        self.headers['Host'] = host
        self.host = 'https://' + host

    def _get_amo_hash(self):
        response = self.session.get(f'{self.host}/api/v4/account?with=amojo_id').json()
        self.amo_hash = response['amojo_id']

    def _create_chat_token(self):
        payload = {'request[chats][session][action]': 'create'}
        response = self.session.post(f'{self.host}/ajax/v1/chats/session', headers=self.headers, data=payload)
        self.chat_token = response.json()['response']['chats']['session']['access_token']

    def create_deal(self):
        url = f'{self.host}/ajax/leads/detail/'
        data = {
            'lead[NAME]': 'AvatarexTgSearch',
            'lead[STATUS]': 62059562,
            'lead[MAIN_USER]': 10133506,
            'lead[PRICE]': '',
            'CFV[1370253]': '',
            'CFV[1335927]': '',
            'CFV[1335929]': '',
            'CFV[1335931]': '',
            'CFV[1335933]': '',
            'CFV[1335935]': '',
            'CFV[1335937]': '',
            'CFV[1335939]': '',
            'CFV[1335941]': '',
            'CFV[1335943]': '',
            'CFV[1335945]': '',
            'CFV[1335947]': '',
            'CFV[1335949]': '',
            'CFV[1335951]': '',
            'CFV[1335953]': '',
            'CFV[1335955]': '',
            'CFV[1335957]': '',
            'CFV[1335959]': '',
            'CFV[1335961]': '',
            'CFV[1335963]': '',
            'leadFromCont': 0
        }
        response = self.session.post(url, headers=self.headers, data=data).json()
        deal_id = response['id']
        return deal_id

    def add_person(self, deal_id):
        data = {
            'contact[MAIN_USER_ID]': 10133506,
            'lead[ID]': deal_id,
            'lead[NAME]': '',
            'ELEMENT_TYPE': 1,
            'CFV[1335919][buEhoDeaUv][DESCRIPTION]': 798697,
            'CFV[1335919][buEhoDeaUv][VALUE]': '',
            'CFV[1335921][ZiMHOKbdos][DESCRIPTION]': 798709,
            'CFV[1335921][ZiMHOKbdos][VALUE]': '',
            'CFV[1335917]': '',
            'contact[NAME]': 'Manager2',
            'lead[ID]': deal_id,
            'lead[PIPELINE_ID]': 'undefined',
            'lead[STATUS]': 62059562
        }
        url = f'{self.host}/private/ajax/contacts/add_person/?ACTION=ADD_PERSON&template=twig&from_lead=Y'
        response = self.session.post(url, headers=self.headers, data=data).json()

    def auth(self) -> bool:
        self._create_session()
        response = self.session.post('https://www.amocrm.ru/oauth2/authorize', data={
            'csrf_token': self.csrf_token,
            'username': self.login,
            'password': self.password
        }, headers=self.headers)
        if response.status_code != 200:
            return False
        self.access_token = response.cookies.get('access_token')
        self.refresh_token = response.cookies.get('refresh_token')
        self.headers['access_token'], self.headers['refresh_token'] = self.access_token, self.refresh_token
        self._get_host()
        self._get_amo_hash()
        self._create_chat_token()
        return True

    def set_field_by_name(self, deal_id):
        url = f'{self.host}/ajax/leads/detail/'

        data = {
            f'CFV[1370253]': 1,
            'lead[STATUS]': 62059562,
            'ID': deal_id
        }
        print(data)
        response = self.session.post(url, headers=self.headers, data=data)
        print(response.json())

    def add_sadist(self, deal_id, username):
        from selenium import webdriver
        from selenium.webdriver.common.by import By

        driver = webdriver.Chrome()
        driver.get(f'{self.host}/leads/detail/{deal_id}')

        driver.find_element(By.NAME, 'username').send_keys(login)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.ID, 'auth_submit').click()
        time.sleep(3)
        switcher = driver.find_element(By.CLASS_NAME, 'feed-compose-switcher')
        ActionChains(driver).move_to_element(switcher).perform()
        time.sleep(3)
        driver.find_element(By.CLASS_NAME, 'js-switcher-chat').click()
        time.sleep(3)
        driver.find_element(By.CLASS_NAME, 'feed-compose__message').click()
        time.sleep(1)
        driver.find_element(By.ID, 'radist_telegram_create_chat_button').click()
        time.sleep(5)
        driver.find_element(By.ID, 'radist_telegram_modal_username_input').send_keys(username)
        driver.find_element(By.ID, 'radist_telegram_modal_create_chat_button').click()
        time.sleep(3)
        driver.close()


def execute(username):
    amo_connection = AmoConnect(login, password)
    is_connected: bool = amo_connection.auth()
    print(is_connected)
    deal_id = amo_connection.create_deal()
    print(deal_id)
    amo_connection.add_person(deal_id)
    amo_connection.set_field_by_name(deal_id)
    amo_connection.add_sadist(deal_id, username)
