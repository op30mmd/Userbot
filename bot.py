from datetime import datetime
import pytz
import socket
import os
import requests
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
from telethon.tl.functions.account import UpdateProfileRequest
import shlex
import shelve
import subprocess
import tempfile
import re
import time

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
        try:
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
        except subprocess.CalledProcessError as e:
            await client.edit_message(event.chat_id, event.id, f'```\nNon-Zero exit:\n{e}\n```')


    elif command_name == 'upload':
        if len(command_parts) < 2:
            await event.reply('usage: .upload <path>')
            return
        
        try:
            file_path = os.path.expandvars(os.path.expanduser(command_parts[1]))
            if not os.path.isfile(file_path):
                await event.reply(f"The file {file_path} does not exist on the server.")
                logger.error(f"The file {file_path} does not exist.")
                return
            path = command_parts[1]
            await client.edit_message(event.chat_id, event.id, f'Uploading file: `{path}`')
            await client.send_file(event.chat_id, path)
            await event.reply('Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'download':
        if not event.is_reply and len(command_parts) < 2:
            await event.reply('Usage: .download <reply> or <link>')
            return
        
        if event.is_reply:
            try:
                message = await event.get_reply_message()
                f_name = message.file.name
                await client.edit_message(event.chat_id, event.id, f'Downloading file: `{f_name}`')
                await client.download_media(message)
                await event.reply('Success')
            except Exception as e:
                await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

        elif len(command_parts) == 2:
            try:
                txt = command_parts[1]
                pat = r'https:\/\/t\.me\/([a-zA-Z0-9_]+)\/([0-9]+)'
                ree = re.search(pat, txt)
                if ree:
                    username = ree.group(1)
                    msgid = int(ree.group(2))
                    await client.edit_message(event.chat_id, event.id, f'Downloading https://t.me/{username}/{msgid}')
                    msg = await client.get_messages(username, ids=msgid)
                    await client.download_media(msg)
                    await event.reply("success")
            except Exception as e:
                await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'del':
        if not event.is_reply:
            await event.reply('Usage: .del <reply>')
            return

        try:
            message = await event.get_reply_message()
            await client.delete_messages(event.chat_id, [message.id])
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'promote':
        if not event.is_reply:
            await event.reply('Usage: .promote <reply>')
            return
        
        try:
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
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'demote':
        if not event.is_reply:
            await event.reply('Usage: .demote <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Demoting user...')
            await client.edit_admin(
                event.chat_id,
                message.sender_id,
                is_admin=False
            )
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'kick':
        if not event.is_reply:
            await event.reply('Usage: .kick <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Kicking user...')
            await client.kick_participant(event.chat_id, message.sender_id)
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'ban':
        if not event.is_reply:
            await event.reply('Usage: .ban <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Banning user...')
            await client.edit_permissions(event.chat_id, message.sender_id, view_messages=False)
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'unban':
        if not event.is_reply:
            await event.reply('Usage: .unban <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Unbanning user...')
            await client.edit_permissions(event.chat_id, message.sender_id)
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'id':
        if not event.is_reply:
            await event.reply('Usage: .id <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            gpeer = await client.get_entity(message.sender_id)
            f_name = utils.get_display_name(gpeer)
            await client.edit_message(event.chat_id, event.id, f"{f_name}'s ID: `{message.sender_id}`")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'pin':
        if not event.is_reply:
            await event.reply('Usage: .pin <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Pinning message...')
            await message.pin(notify=False)
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'unpin':
        if not event.is_reply:
            await event.reply('Usage: .unpin <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Unpinning message...')
            await message.unpin()
            await client.edit_message(event.chat_id, event.id, 'Success')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'ping':
        await event.reply(f"**Pong!**\n```\nBot Is Alive And Running...\n```")

    elif command_name == 'help':
        await event.reply(f'`{COMMAND_PREFIX}echo` <message>\n'
                          f'`{COMMAND_PREFIX}run` <command>\n'
                          f'`{COMMAND_PREFIX}upload` <path>\n'
                          f'`{COMMAND_PREFIX}download` <reply>\n'
                          f'`{COMMAND_PREFIX}del` <reply>\n'
                          f'`{COMMAND_PREFIX}promote` <reply>\n'
                          f'`{COMMAND_PREFIX}demote` <reply>\n'
                          f'`{COMMAND_PREFIX}kick` <reply>\n'
                          f'`{COMMAND_PREFIX}ban` <reply>\n'
                          f'`{COMMAND_PREFIX}unban` <reply>\n'
                          f'`{COMMAND_PREFIX}id` <reply>\n'
                          f'`{COMMAND_PREFIX}pin` <reply>\n'
                          f'`{COMMAND_PREFIX}unpin` <reply>\n'
                          f'`{COMMAND_PREFIX}ping`\n'
                          f'`{COMMAND_PREFIX}block` <reply>\n'
                          f'`{COMMAND_PREFIX}unblock` <reply>\n'
                          f'`{COMMAND_PREFIX}time`\n'
                          f'`{COMMAND_PREFIX}tn` (Start Manually)\n'
                          f'`{COMMAND_PREFIX}stop` (stops the timename loop)\n'
                          f'`{COMMAND_PREFIX}setem` <reply to emoji> (set emoji status)\n'
                          f'`{COMMAND_PREFIX}msginfo` <reply>\n'
                          f"`{COMMAND_PREFIX}info` <reply>\n"
                          f"`{COMMAND_PREFIX}ipinfo`\n"
                          f"`{COMMAND_PREFIX}getmsg` <link>\n"
                          f"`{COMMAND_PREFIX}dlst` <link> | Download story\n"
                          f"`{COMMAND_PREFIX}dex` | crypto price (coinbase)\n"
                          f"`{COMMAND_PREFIX}git` <Github repo link> | downloads and uploads a github repo to telegram"
                          )

    elif command_name == 'block':
        if not event.is_reply:
            await event.reply('Usage: .block <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            peer = await client.get_entity(message.sender_id)
            f_name = utils.get_display_name(peer)
            await client.edit_message(event.chat_id, event.id, 'Blocking user...')
            deb = await client(functions.contacts.BlockRequest(
            id=message.sender_id
            ))
            await client.edit_message(event.chat_id, event.id, f'Success Blocking User: {f_name}\nStatus: {deb}')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'unblock':
        if not event.is_reply:
            await event.reply('Usage: .unblock <reply>')
            return
        
        try:
            message = await event.get_reply_message()
            peer = await client.get_entity(message.sender_id)
            f_name = utils.get_display_name(peer)
            await client.edit_message(event.chat_id, event.id, 'Unblocking user...')
            deb = await client(functions.contacts.UnblockRequest(
            id=message.sender_id
            ))
            await client.edit_message(event.chat_id, event.id, f'Success Unblocking User: {f_name}\nStatus: {deb}')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`')

    elif command_name == 'time':
        r = requests.get('https://api.keybit.ir/time')
        t = r.json()["time24"]["full"]["en"]
        await client.edit_message(event.chat_id, event.id, f"Time Zone: Asia/Tehran\nCurrent Time: {t}\nBack-end: API")

    elif command_name == 'setem':
        if not event.is_reply:
            await event.reply('Usage: .setem <reply>')
            return

        pat = r'\[\s*(\d+)\s*\]'  # This pattern allows optional spaces inside the brackets

        try:
            message = await event.get_reply_message()
            await client.edit_message(event.chat_id, event.id, 'Processing...')
            await client.forward_messages('@GetEmojiIdBot', message)
            await asyncio.sleep(1)
            msg = await client.get_messages('@GetEmojiIdBot', limit=1)
            f_msg = msg[0]
            match = re.search(pat, f_msg.text)
            doc_id = int(match.group(1))
            await client(functions.account.UpdateEmojiStatusRequest(
                        emoji_status=types.EmojiStatus(
                                document_id=doc_id
                            )
                    ))
            await client.edit_message(event.chat_id, event.id, 'Success Setting Emoji Status')
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f'Error: `{e}`\nDebug: `{f_msg.text}`')

    elif command_name == 'purgeme':
        try:
            async for message in client.iter_messages(event.chat_id):
                if message.sender_id == owner:
                    await client.delete_messages(event.chat_id, [message.id])
        except Exception as e:
            await client.send_message(-1002377481815, f"Error: `{e}`")

    elif command_name == 'msginfo':
        if not event.is_reply:
            await event.reply("Usage: .msginfo <reply>")
            return
        
        try:
            msg = await event.get_reply_message()
            if msg.views != None:
                await client.edit_message(event.chat_id, event.id, f"**Message info (Channel)**\n\nMessage ID: `{msg.id}`\nMentioned?: `{msg.mentioned}`\nMedia Unread?: `{msg.media_unread}`\nPost?: `{msg.post}`\nScheduled?: `{msg.from_scheduled}`\nLegacy?: `{msg.legacy}`\nPinned?: `{msg.pinned}`\nForwardable?: `{msg.noforwards}`\nPeerID: `{msg.peer_id.channel_id}`\nViews: `{msg.views}`\nInline BotID: `{msg.via_bot_id}`\nForwards: `{msg.forwards}`\nReplies: `{msg.replies.replies}`\nEdit Date: `{msg.edit_date}`\nPost Author: `{msg.post_author}`\nChannel ID: `-100{msg.from_id.channel_id}`")
            elif msg.views == None:
                await client.edit_message(event.chat_id, event.id, f"**Message info (User)**\n\nMessage ID: `{msg.id}`\nMentioned?: `{msg.mentioned}`\nMedia Unread?: `{msg.media_unread}`\nScheduled?: `{msg.from_scheduled}`\nLegacy?: `{msg.legacy}`\nPinned?: `{msg.pinned}`\nForwardable?: `{msg.noforwards}`\nOffline?: `{msg.offline}`\nSenderID (This MSG): `{org_id}`\nPeerID: `{msg.peer_id.channel_id}`\nUserID: `{msg.from_id.user_id}`\nInline BotID: `{msg.via_bot_id}`\nEdit Date: `{msg.edit_date}`")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")

    elif command_name == "info":
        if not event.is_reply:
            await event.reply("Usage: .info <reply>")
            return

        try:
            msg = await event.get_reply_message()
            info = await client.get_entity(msg.from_id)
            if info.status:
                if hasattr(info.status, 'was_online'):
                    status = f"Offline: {info.status.was_online}"
                elif hasattr(info.status, 'expires'):
                    status = "Status: Online"
                elif hasattr(info.status, 'by_me'):
                    status = "Status: Recently"
                else:
                    status = f"Status: {info.status}"
            else:
                status = "Status: N/A"

            if info.premium:
                if info.color is None:
                    color = "Color: N/A"
                else:
                    color_code = info.color.color if info.color else "N/A"
                    color_emoji_id = info.color.background_emoji_id if info.color else "N/A"
                    profile_color_code = info.profile_color.color if info.profile_color else "N/A"
                    profile_emoji_id = info.profile_color.background_emoji_id if info.profile_color else "N/A"
        
                color = f"""ColorCode: {color_code}
ColorEmojiID: `{color_emoji_id}`
ProfileColorCode: `{profile_color_code}`
BGEmojiID: `{profile_emoji_id}`"""
    
                additional_premium_info = f"""Contact Require Premium?: `{info.contact_require_premium}`
EmojiStatusDocID: `{info.emoji_status.document_id}`
{color}
"""
            else:
                additional_premium_info = ""

            message = f"""**Info (User)**
```Values with None Are not for Users```

ID: `{info.id}`
Name: `{info.first_name}`
Username: `{info.username}`
Premium?: `{info.premium}`
Self?: `{info.is_self}`
Contact?: `{info.contact}`
Mutual Contact?: `{info.mutual_contact}`
Deleted?: `{info.deleted}`
Bot?: `{info.bot}`
Verified?: `{info.verified}`
Restricted?: `{info.restricted}`
Support?: `{info.support}`
Scam?: `{info.scam}`
Fake?: `{info.fake}`
Close Friend?: `{info.close_friend}`
Stories Hidden?: `{info.stories_hidden}`
Stories Unavailable?: `{info.stories_unavailable}`
Business Bot?: `{info.bot_business}`
Bot Has Main App?: `{info.bot_has_main_app}`
{status}
Bot Info Ver.: `{info.bot_info_version}`
Inline Placeholder: `{info.bot_inline_placeholder}`
UserLangCode: `{info.lang_code}`
MaxStoryID: `{info.stories_max_id}`
{additional_premium_info}
"""

            await client.edit_message(event.chat_id, event.id, message)
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")

    elif command_name == 'denyreqs':
        await client.edit_message(event.chat_id, event.id, "Processing...")
        try:
            chatid = event.chat_id
            peerch = await client.get_entity(chatid)
            await client(functions.messages.HideAllChatJoinRequestsRequest(
                   peer=peerch,
                   approved=False,
                    ))
            await event.reply("Success")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")
    
    elif command_name == 'ipinfo':
        await client.edit_message(event.chat_id, event.id, "Processing...")
        try:
            r = requests.get("http://wtfismyip.com/json")
            if r.status_code == 200:
                ip = r.json()["YourFuckingIPAddress"]
                loc = r.json()["YourFuckingLocation"]
                host = r.json()["YourFuckingHostname"]
                isp = r.json()["YourFuckingISP"]
                city = r.json()["YourFuckingCity"]
                country = r.json()["YourFuckingCountry"]
                ccode = r.json()["YourFuckingCountryCode"]
                await client.edit_message(event.chat_id, event.id, f"**ip info (current server)**\n\nIP: `{ip}`\nLocation: `{loc}`\nHostname: `{host}`\nISP: `{isp}`\nCity: `{city}`\nCountry: `{country}`\nCountryCode: `{ccode}`")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")

    elif command_name == 'getmsg':
        if len(command_parts) < 2:
            await client.edit_message(event.chat_id, event.id, "Usage: .getmsg <chat or channel> <message id>")
            return
        try:
            pat = r'https:\/\/t\.me\/([a-zA-Z0-9_]+)\/([0-9]+)'
            ree = re.search(pat, command_parts[1])
            if ree:
                username = ree.group(1)
                msgid = ree.group(2)
                async for message in client.iter_messages(username, ids=int(msgid)):
                    await client.edit_message(event.chat_id, event.id, f"**Message Text**\n\nchat or channel: {username}\nMessage ID: {msgid}\n\nMessage:\n{message.text}")
            else:
                await client.edit_message(event.chat_id, event.id, "Incorrect Link Format or link not provided")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")
    
    elif command_name == 'tn':
        await client.edit_message(event.chat_id, event.id, "Started TimeName")
        try:
            tz = pytz.timezone('Asia/Tehran')
            owner_name = "Vulkan (Formerly Mamat)"
            stop_flag = False
            while not stop_flag:
                now = datetime.now(tz)
                current_time = now.strftime('%H:%M')
                await asyncio.sleep(30)
                await client(UpdateProfileRequest(first_name=f"{owner_name} | {current_time}"))

                if command_name == 'stop':
                    await client.edit_message(event.chat_id, event.id, "Stopped autoname")
                    stop_flag = True  # Set flag to exit loop
                    break
        except Exception as e:
            await client.send_message(-1002377481815, f"Error: `{e}`")

    elif command_name == 'dlst':
        if len(command_parts) < 2:
            await client.edit_message(event.chat_id, event.id, "Usage: .dlst <link>")
            return

            
        pat = r'https://t\.me/([a-zA-Z0-9_]+)/s/([0-9]+)'
        ms = re.findall(pat, command_parts[1])
        if ms:
            for mats in ms:
                username = mats[0]
                id = int(mats[1])
                await client.edit_message(event.chat_id, event.id, "Downloading...")

                try:
                    stories = (
                        await client(GetStoriesByIDRequest(username, [id]))
                            ).stories
                    story_file = await client.download_media(stories[0].media)
                    await client.edit_message(event.chat_id, event.id, 'Done.\nUploading...')
                    await client.send_file(event.chat_id, story_file)
                    await event.reply('Done.')
                except Exception as e:
                    await client.edit_message(event.chat_id, event.id, f"Error: `{e}`")
    
    elif command_name == 'dex':
        if len(command_parts) < 2:
            await event.reply("usage: .dex <coin>")
            return
        coin = command_parts[1]
        reqbuy = requests.get(f"https://api.coinbase.com/v2/prices/{coin}-USD/buy")
        resbuy = reqbuy.json()
        reqsell = requests.get(f"https://api.coinbase.com/v2/prices/{coin}-USD/sell")
        ressell = reqsell.json()

        if reqbuy.status_code == 200 and reqsell.status_code == 200:
            buyp = resbuy["data"]["amount"]
            sellp = ressell["data"]["amount"]
            await client.edit_message(event.chat_id, event.id, f"**{coin}'s prices (CoinBase):**\n\nBuy Price: {buyp}\nSell price: {sellp}")
        else:
            await client.edit_message(event.chat_id, event.id, f"Error!\nCode: {reqbuy.status_code} | {reqsell.status_code}")

    elif command_name == 'git':
        if len(command_parts) < 2:
            await event.reply("usage: .git <repo>")
            return
        
        repo = command_parts[1]

        try:
            clone = subprocess.check_output(f"git clone {repo}", shell=True).decode('utf-8')
            reponame = r'^https://github.com/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)$'
            match = re.match(reponame, repo)
            username = match.group(1)
            repon = match.group(2)
            subprocess.check_output(f"zip -r {repon}.zip {repon}", shell=True)
            await client.edit_message(event.chat_id, event.id, f"**Processing...**")
            await client.send_file(event.chat_id, f"{repon}.zip", caption=f"**success cloning {repon} from {username}**")
        except Exception as e:
            await client.edit_message(event.chat_id, event.id, f"Error: {e}")
client.start()
client.run_until_disconnected()
