import requests


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
amo_connection = AmoConnect(login, password)
is_connected: bool = amo_connection.auth()
print(is_connected)