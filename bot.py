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
COMMAND_PREFIX = "."

client = TelegramClient(StringSession(os.environ.get("SESSION")), os.environ.get("API_ID"), os.environ.get("API_HASH"))

@client.on(events.NewMessage)
async def get(event):
    r_txt = event.raw_text.strip()
    sender = await event.get_sender()
    org_id = sender.id
    command_parts = shlex.split(r_txt)
    command_name = command_parts[0][len(COMMAND_PREFIX):].lower()
    owner = 1630778333
    if org_id != owner:
        return
    if not r_txt.startswith(COMMAND_PREFIX):
        return  # Not a command
    if command_name == 'echo':
        if len(command_parts) < 2:
            await event.reply('متن کیریتو وارد کن جلوی .echo')
        await event.reply(command_parts[1])

client.start()
client.run_until_disconnected()
