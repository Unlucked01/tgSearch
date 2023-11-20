import gspread
from oauth2client.service_account import ServiceAccountCredentials

table_name = 'Chats Saver For Vladimir'


def read():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(table_name)

    all_sheets = spreadsheet.worksheets()

    # Словарь для хранения данных из каждого листа
    all_data = {}

    # Читаем данные из каждого листа (кроме первого)
    for sheet in all_sheets[1:]:  # Начинаем с индекса 1, чтобы пропустить первый лист
        data = {'titles': sheet.col_values(1)[1::], 'keywords': sheet.col_values(2)[1::], 'chat_id': sheet.col_values(3)[1]}
        all_data[sheet.title] = data

    return all_data

