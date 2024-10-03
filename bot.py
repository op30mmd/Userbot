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
from telethon.tl.custom import ParticipantPermissions
import shlex
import subprocess
import tempfile
import re

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
COMMAND_PREFIX = "."

client = TelegramClient(StringSession(os.environ.get("SESSION")), int(os.environ.get("API_ID")), os.environ.get("API_HASH"))

@client.on(events.NewMessage)
async def userbot(event):
    sender = await event.get_sender()
    org_id = sender.id
    owner = 1630778333
    if org_id != owner:
        return
    r_txt = event.raw_text.strip()
    if not r_txt.startswith(COMMAND_PREFIX):
        return  # Not a command
    command_parts = shlex.split(r_txt)
    command_name = command_parts[0][len(COMMAND_PREFIX):].lower()

    if command_name == 'echo':
        if len(command_parts) < 2:
            await event.reply('Usage: .echo <message>')
            return
        await event.reply(command_parts[1:])

    elif command_name == 'run':
        if len(command_parts) < 2:
            await event.reply('Usage: .run <command>')
            return
        cmd = command_parts[1:]
        str_cmd = ' '.join(cmd)
        await client.edit_message(event.chat_id, event.id, f'Running Command: ```{str_cmd}```...')
        run = subprocess.check_output(str_cmd, shell=True).decode('utf-8')
        if len(run) < 4000:
            await event.reply(f"```INPUT:\n{str_cmd}```\n```OUTPUT:\n{run}```")
        else:
            with open('output.txt', 'w') as f:
                f.write(run)
            await client.send_file(event.chat_id, 'output.txt', caption="```\nOutput was too long\n```")


    elif command_name == 'upload':
        if len(command_parts) < 2:
            await event.reply('usage: .upload <path>')
            return
        file_path = os.path.expandvars(os.path.expanduser(command_parts[1]))
        if not os.path.isfile(file_path):
            await event.reply(f"The file {file_path} does not exist on the server.")
            logger.error(f"The file {file_path} does not exist.")
            return
        path = command_parts[1]
        await client.edit_message(event.chat_id, event.id, f'Uploading file: `{path}`')
        await client.send_file(event.chat_id, path)
        await event.reply('Success')

    elif command_name == 'download':
        if not event.is_reply:
            await event.reply('Usage: .download <reply>')
            return
        message = await event.get_reply_message()
        f_name = message.file.name
        await client.edit_message(event.chat_id, event.id, f'Downloading file: `{f_name}`')
        await client.download_media(message)
        await event.reply('Success')

    elif command_name == 'del':
        if not event.is_reply:
            await event.reply('Usage: .del <reply>')
            return
        message = await event.get_reply_message()
        await client.delete_messages(event.chat_id, [message.id])
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'promote':
        if not event.is_reply:
            await event.reply('Usage: .promote <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Promoting user...')
        await client.edit_admin(
            event.chat_id,
            message.sender_id,
            change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False  # Adjust as needed
        )
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'demote':
        if not event.is_reply:
            await event.reply('Usage: .demote <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Demoting user...')
        await client.edit_admin(
            event.chat_id,
            message.sender_id,
            is_admin=False
        )
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'kick':
        if not event.is_reply:
            await event.reply('Usage: .kick <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Kicking user...')
        await client.kick_participant(event.chat_id, message.sender_id)
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'ban':
        if not event.is_reply:
            await event.reply('Usage: .ban <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Banning user...')
        await client.edit_permissions(event.chat_id, message.sender_id, view_messages=False)
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'unban':
        if not event.is_reply:
            await event.reply('Usage: .unban <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Unbanning user...')
        await client.edit_permissions(event.chat_id, message.sender_id)
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'id':
        if not event.is_reply:
            await event.reply('Usage: .id <reply>')
            return
        message = await event.get_reply_message()
        gpeer = await client.get_entity(message.sender_id)
        f_name = utils.get_display_name(gpeer)
        await client.edit_message(event.chat_id, event.id, f"{f_name}'s ID: `{message.sender_id}`")

    elif command_name == 'pin':
        if not event.is_reply:
            await event.reply('Usage: .pin <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Pinning message...')
        await message.pin(notify=False)
        await client.edit_message(event.chat_id, event.id, 'Success')

    elif command_name == 'unpin':
        if not event.is_reply:
            await event.reply('Usage: .unpin <reply>')
            return
        message = await event.get_reply_message()
        await client.edit_message(event.chat_id, event.id, 'Unpinning message...')
        await message.unpin()
        await client.edit_message(event.chat_id, event.id, 'Success')

    
client.start()
client.run_until_disconnected()
