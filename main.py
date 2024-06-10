import configparser
import datetime
import time
import asyncio
from db import async_session, User
from sqlalchemy.future import select

from pyrogram import Client, filters

from db import Session, User, init_db

config = configparser.ConfigParser()

config.read('config.ini')

api_id = config['pyrogram']['api_id']
api_hash = config['pyrogram']['api_hash']

app = Client("my_account", api_id=api_id, api_hash=api_hash)

trigger_words = ["прекрасно", "ожидать"]


def check_triggers(text):
    words = text.split()
    for word in trigger_words:
        if word.lower() in [w.lower() for w in words]:
            return True
    return False



@app.on_message(filters.private & filters.incoming)
async def handle_private_message(client, message):

    user_id = message.from_user.id
    text = message.text
    ready_users = await get_ready_users()

    async with async_session() as session:
        user = await session.execute(select(User).filter_by(id=user_id))
        user = user.scalars().first()

        if check_triggers(text):
            print(f"Получено сообщение с триггером от пользователя {user_id}: {text}")
            if user:
                user.status = 'dead'
                user.status_updated_at = datetime.datetime.utcnow()
                await session.commit()
        else:
            if user and user in ready_users:
                last_message_time = user.last_message_time
                if last_message_time:
                    time_delta = datetime.datetime.utcnow() - last_message_time

                    if time_delta.total_seconds() >= 600:
                        user.last_message_time = datetime.datetime.utcnow()
                        await session.commit()

                        if time_delta.total_seconds() >= 780:
                            user.last_message_time = datetime.datetime.utcnow()
                            await session.commit()
                else:
                    await asyncio.sleep(360)
                    user.last_message_time = datetime.datetime.utcnow()
                    await session.commit()
            else:
                await asyncio.sleep(360)
                new_user = User(id=user_id, status='alive')
                session.add(new_user)
                await session.commit()
                user.last_message_time = datetime.datetime.utcnow()
                await session.commit()


async def get_ready_users():
    while True:
        async with async_session() as session:
            result = await session.execute(select(User).filter_by(status='alive'))
            ready_users = result.scalars().all()
            return ready_users
        await asyncio.sleep(5)   


async def main():
    await init_db()
    app.run()

if __name__ == "__main__":
    asyncio.run(main())
