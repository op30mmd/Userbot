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
async def find_owner(event):
    sender = await event.get_sender()
    org_id = sender.id
    owner = 1630778333
    if org_id != owner:
        return

@client.on(events.NewMessage(r'^\.echo (.+)$'))
async def get(event):
    text = event.pattern_match.group(1)
    num = len(event.pattern_match.groups())

    if num < 1:
        await event.reply("اینجوری استفاده کن  کودن: `.echo <text>`")
        return
    await event.reply(text)
    
    #if not r_txt.startswith(COMMAND_PREFIX):
        #return  # Not a command

client.start()
client.run_until_disconnected()
