import os
import asyncio
import logging
from telethon import TelegramClient, events, Button, utils
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from telethon import functions, types
from telethon.tl.types import Message
from telethon.tl.types import UpdateBotNewBusinessMessage
from telethon.tl.functions import InvokeWithBusinessConnectionRequest
from telethon.tl.functions.stories import GetStoriesByIDRequest
import shlex
import subprocess
import tempfile
import re


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

client = TelegramClient(StringSession(os.environ.get("SESSION", "")), os.environ.get("API_ID", ""), os.environ.get("API_HASH", ""))
async def main():
    await client.start()
    print(await client.get_me())
    await client.run_until_disconnected()

@client.on(events.NewMessage(pattern=r'^/get\s+(\S+)\s+(\d+)$'))
async def get(event):
    chat = event.pattern_match.group(1)
    msg_id = int(event.pattern_match.group(2))
    num_args = len(event.pattern_match.groups())

    if num_args != 2:
        await event.reply('Invalid pattern. usage: /get <chat_id> <msg_id>')
        return

    try:
        gmsg = await client.get_messages(chat, msg_id)
        await event.reply(gmsg)
    except Exception as e:
        await event.reply(str(e))
