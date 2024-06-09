import configparser
import datetime
import time
import asyncio

from pyrogram import Client, filters

from db import Session, User, init_db

config = configparser.ConfigParser()

config.read('config.ini')

api_id = config['pyrogram']['api_id']
api_hash = config['pyrogram']['api_hash']

app = Client("my_account", api_id=api_id, api_hash=api_hash)

trigger_words = ["прекрасно", "ожидать"]


def check_triggers(text):
    for word in trigger_words:
        if word in text:
            return True
    return False


def send_message(user_id, text):
    app.send_message(user_id, text)


@app.on_message(filters.private & filters.incoming)
def handle_private_message(client, message):
    user_id = message.from_user.id
    text = message.text

    if check_triggers(text.lower()):
        print(
            f"Получено сообщение с триггером от пользователя {user_id}: {text}")
        session = Session()
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.status = 'finished'
            user.status_updated_at = datetime.datetime.utcnow()
            session.commit()
        else:
            print(f"Пользователь {user_id} не найден в базе данных")
    else:
        print(f"Получено сообщение от пользователя {user_id}: {text}")


async def check_ready_users():
    while True:
        session = Session()
        ready_users = session.query(User).filter_by(status='finished').all()
        for user in ready_users:
            print(f"Пользователь {user.id} готов к получению сообщения")
            await send_message(user.id, "Ваше сообщение готово")
            user.status = 'notified'
            user.status_updated_at = datetime.datetime.utcnow()
            session.commit()
        session.close()
        await asyncio.sleep(5)  # Пауза между проверками


def main():
    init_db()
    app.run()
    asyncio.create_task(check_ready_users())


if __name__ == "__main__":
    main()
