from telethon.sync import TelegramClient
from telethon.sessions import StringSession, MemorySession, SQLiteSession

api_id = 24041156
api_hash = '1d7e76a039dfc4280b1c5fbfcdd99f4c'

string = """1ApWapzMBuyI69o-wW9pp_LE_PtjvSSW-_CeHdmXIJVN6zD2_cTv87Zm4f8SMP4JymgIlSuFKlMaEKrYAiAdZdVQ71rZmFNO1-KkzOZKTeXWdcJAmXqdgnChz9UuzhiM9enwk8eZrvC9LNpu9W5Ziy1X-bY_GGU6niWSMV-dXC0gp1rI_AC4mDo5u7WrmcU1LXAcWMsNKQt4-Uk6av-8CKmTAXxOGCaFPybpcFRkPrghTdMgrNvyYDv0Xre9Wo2ivHa0msvIsbzdicmu-qMfFgtYN2_-OciXJ55WPxqX-IHoqyoP5xLJm_UqQSJ-Wn1wqN7LY_SB5FXamkOV7yO6l0_Fgkv2ifEs=
"""

with TelegramClient(StringSession(string=string), api_id=api_id, api_hash=api_hash) as client:
    # print(client.session.save())
    client.loop.run_until_complete(client.send_message('me', 'Hi'))



