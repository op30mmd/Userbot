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

client = TelegramClient(StringSession(os.environ.get("SESSION")), os.environ.get("API_ID"), os.environ.get("API_HASH"))

@client.on(events.NewMessage(pattern='/hi'))
async def get(event):
    await event.reply('hi')

client.start()
client.run_until_disconnected()
