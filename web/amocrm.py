import json

import requests
import bs4


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
    deal_id = ''
    pipeline = ''

    def __init__(self, user_login: str, user_password: str, host='', token='', deal_id=0, pipeline=0):
        self.login = user_login
        self.password = user_password
        self.host = host
        self.amo_hash = token
        self.deal_id = deal_id
        self.pipeline = pipeline
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

    def _create_field(self, name):
        url = f'{self.host}/ajax/settings/custom_fields/'
        data = {
            'action': 'apply_changes',
            'cf[add][0][element_type]': 2,
            'cf[add][0][sortable]': True,
            'cf[add][0][groupable]': True,
            'cf[add][0][predefined]': False,
            'cf[add][0][type_id]': 1,
            'cf[add][0][name]': name,
            'cf[add][0][disabled]': '',
            'cf[add][0][settings][formula]': '',
            'cf[add][0][pipeline_id]': 0
        }
        self.session.post(url, data=data, headers=self.headers)

    def get_params_information(self, fields: list):
        result = {}
        url = f'{self.host}/leads/detail/{self.deal_id}'
        response = self.session.get(url)
        soup = bs4.BeautifulSoup(response.text, features='html.parser')
        #  print(soup)

        for field in soup.find_all('div', {'class': 'linked-form__field linked-form__field-text'}):
            label = field.find('div', {'class': 'linked-form__field__label'}).text.strip()
            value = field.find('div', {'class': 'linked-form__field__value'}).find('input')['value'].strip()
            index = field.get('data-id')
            if label in fields:
                if value == '':
                    value = None

                result[label] = {'active': value, 'values': [], 'type': 'field', 'id': index}

        selects = soup.find_all('div', {'class': 'linked-form__field linked-form__field-select'})
        for select in selects:
            k = select.find('div', {'class': 'linked-form__field__label'}).text
            v = select.find('span', {'class': 'control--select--button-inner'}).text.strip()
            index = select.get('data-id')
            if k in fields:
                result[k] = {'active': v,
                             'values': [],
                             'type': 'select',
                             'id': index}
                if result[k]['active'] == 'Выбрать':
                    result[k]['active'] = None
                for v in select.find_all('li', {'class': 'control--select--list--item'}):
                    index = v.get('data-value')
                    if v.text.strip() != 'Выбрать':
                        result[k]['values'].append({'value': v.text.strip(), 'id': index})

        need_update = False
        for field in fields:
            if field not in result.keys():
                self._create_field(field)
                need_update = True
        if need_update:
            return self.get_params_information(fields)
        return result

    def set_field_by_name(self, name, value, amo_fields):
        url = f'{self.host}/ajax/leads/detail/'
        field = amo_fields[name]
        active_value = value

        if field['type'] == 'select':
            for f in field['values']:
                if f['value'] == value:
                    active_value = f['id']

        data = {
            f'CFV[{field["id"]}]': active_value,
            'lead[STATUS]': '',
            'lead[PIPELINE_ID]': self.pipeline,
            'ID': self.deal_id
        }
        response = self.session.post(url, data=data)

    def send_message(self, message: str, chat_id: str):
        headers = {'X-Auth-Token': self.chat_token}
        url = f'https://amojo.amocrm.ru/v1/chats/{self.amo_hash}/' \
              f'{chat_id}/messages?with_video=true&stand=v15'
        requests.post(url, headers=headers, data=json.dumps({"text": message}))

    def create_webhook(self):
        url = 'https://chatgpt.amocrm.ru/ajax/settings/webhooks/set/'
        data = {
            "hook[new_item_1][destination]": 'http://92.255.114.145:8000/api/v1/amocrm/2',
            'hook[new_item_1][add_lead]': 'new_item_1_1',
            'hook[new_item_1][add_contact]': '',
            'hook[new_item_1][add_company]': '',
            'hook[new_item_1][add_customer]': '',
            'hook[new_item_1][add_task]': '',
            'hook[new_item_1][add_unsorted]': 'new_item_1_6',
            'hook[new_item_1][add_message]': 'new_item_1_7',
            'hook[new_item_1][add_talk]': '',
            'hook[new_item_1][update_lead]': 'new_item_1_9',
            'hook[new_item_1][update_contact]': '',
            'hook[new_item_1][update_company]': '',
            'hook[new_item_1][update_customer]': '',
            'hook[new_item_1][update_task]': '',
            'hook[new_item_1][update_unsorted]': '',
            'hook[new_item_1][update_talk]': '',
            'hook[new_item_1][delete_lead]': 'new_item_1_16',
            'hook[new_item_1][delete_contact]': '',
            'hook[new_item_1][delete_company]': '',
            'hook[new_item_1][delete_customer]': '',
            'hook[new_item_1][delete_task]': '',
            'hook[new_item_1][delete_unsorted]': 'new_item_1_21',
            'hook[new_item_1][restore_lead]': '',
            'hook[new_item_1][restore_contact]': '',
            'hook[new_item_1][restore_company]': '',
            'hook[new_item_1][status_lead]': '',
            'hook[new_item_1][responsible_lead]': '',
            'hook[new_item_1][responsible_contact]': '',
            'hook[new_item_1][responsible_company]': '',
            'hook[new_item_1][responsible_customer]': '',
            'hook[new_item_1][responsible_task]': '',
            'hook[new_item_1][note_lead]': '',
            'hook[new_item_1][note_contact]': '',
            'hook[new_item_1][note_company]': '',
            'hook[new_item_1][note_customer]': '',
            'hook[new_item_1][sort]': 1,
            'hook[new_item_1][disabled]': '',
            'hook[new_item_1][new]': 1,
            'hook[new_item_1][id]': "new_item_1"
        }

        response = self.session.post(url, data=data)
        print(response)

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


login = 'appress8@gmail.com'
password = '83xUHS73'
deal_id = 5117051
amo_connection = AmoConnect(login, password, deal_id=deal_id, pipeline=7343546)
is_connected: bool = amo_connection.auth()
fields = ['testField', 'Цвет волос', 'artemggwp']

params = amo_connection.get_params_information(fields)
# amo_connection.set_field_by_name('Цвет волос', 'Зеленый', params)
amo_connection.send_message("Привет!", '2ceb24f8-b7f9-48d3-8a0e-51e78dc53181')
