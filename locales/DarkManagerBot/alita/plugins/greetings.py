# Copyright (C) 2020 - 2021 Divkix. All rights reserved. Source code available under the AGPL.
#
# This file is part of Alita_Robot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from html import escape
from secrets import choice
from traceback import format_exc

from pyrogram import filters, types
from pyrogram.errors import RPCError
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    UserNotParticipant,
)
from pyrogram.types import (
    ChatMemberUpdated,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from alita import MESSAGE_DUMP, OWNER_ID
from alita.bot_class import Alita
from alita.database.antispam_db import GBan
from alita.database.greetings_db import Greetings
from alita.utils.custom_filters import admin_filter, bot_admin_filter, command
from alita.utils.msg_types import Types, get_wlcm_type
from alita.utils.parser import escape_markdown, mention_html
from alita.utils.string import (
    build_keyboard,
    escape_invalid_curly_brackets,
    parse_button,
)

# Initialize
gdb = GBan()


async def escape_mentions_using_curly_brackets_wl(
    m: ChatMemberUpdated,
    n: bool,
    text: str,
    parse_words: list,
) -> str:
    teks = await escape_invalid_curly_brackets(text, parse_words)
    if n:
        user = m.new_chat_member.user if m.new_chat_member else m.from_user
    else:
        user = m.old_chat_member.user if m.old_chat_member else m.from_user
    if teks:
        teks = teks.format(
            first=escape(user.first_name),
            last=escape(user.last_name or user.first_name),
            fullname=" ".join(
                [
                    escape(user.first_name),
                    escape(user.last_name),
                ]
                if user.last_name
                else [escape(user.first_name)],
            ),
            username=(
                "@" + (await escape_markdown(escape(user.username)))
                if user.username
                else (await (mention_html(escape(user.first_name), user.id)))
            ),
            mention=await (mention_html(escape(user.first_name), user.id)),
            chatname=escape(m.chat.title)
            if m.chat.type != "private"
            else escape(user.first_name),
            id=user.id,
        )
    else:
        teks = ""

    return teks


@Alita.on_message(command("cleanwelcome") & admin_filter)
async def cleanwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleanwelcome_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleanwelcome_settings(True)
            await m.reply_text("Aktivləşdirildi!")
            return
        if args[1].lower() == "off":
            db.set_current_cleanwelcome_settings(False)
            await m.reply_text("Deaktivləşdirildi!")
            return
        await m.reply_text("Sən nə etmək istəyirsən??")
        return
    else:
        await m.reply_text(f"Standart vəziyyət:- {status}")
        return
    return


@Alita.on_message(command("cleangoodbye") & admin_filter)
async def cleangdbye(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleangoodbye_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleangoodbye_settings(True)
            await m.reply_text("Aktivləşdirildi!")
            return
        if args[1].lower() == "off":
            db.set_current_cleangoodbye_settings(False)
            await m.reply_text("Deaktivləşləsdirildi!")
            return
        await m.reply_text("Sən nə etmək istəyirsən??")
        return
    else:
        await m.reply_text(f"Standart vəziyyət:- {status}")
        return
    return


@Alita.on_message(command("cleanservice") & admin_filter)
async def cleanservice(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleanservice_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleanservice_settings(True)
            await m.reply_text("Aktivləşdirildi!")
            return
        if args[1].lower() == "off":
            db.set_current_cleanservice_settings(False)
            await m.reply_text("Deaktivləşdirildi!")
            return
        await m.reply_text("Sən nə etmək istəyirsən??")
        return
    else:
        await m.reply_text(f"Standart vəziyyət:- {status}")
        return


@Alita.on_message(command("setwelcome") & admin_filter & bot_admin_filter)
async def save_wlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Limiti keçmə dostum!!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, _ = await get_wlcm_type(m)

    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not msgtype:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_welcome_text(text)
    await m.reply_text("Qarşılama mesajı qeydə alındı!")
    return


@Alita.on_message(command("setgoodbye") & admin_filter & bot_admin_filter)
async def save_gdbye(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Limiti keçmə dostum!!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, _ = await get_wlcm_type(m)

    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not msgtype:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_goodbye_text(text)
    await m.reply_text("Sağollaşma mesajı qeydə alındı!")
    return


@Alita.on_message(command("resetgoodbye") & admin_filter & bot_admin_filter)
async def resetgb(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "{first} qrupu tərk etdi.\nÜmidvaram yenidən gələcəksən 🥲!"
    db.set_goodbye_text(text)
    await m.reply_text("Ok Done!")
    return


@Alita.on_message(command("resetwelcome") & admin_filter & bot_admin_filter)
async def resetwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "Salam {first}, {chatname} xoşgəldin!"
    db.set_welcome_text(text)
    await m.reply_text("Done!")
    return


@Alita.on_message(filters.service & filters.group, group=59)
async def cleannnnn(_, m: Message):
    db = Greetings(m.chat.id)
    clean = db.get_current_cleanservice_settings()
    try:
        if clean:
            await m.delete()
    except Exception:
        pass


@Alita.on_chat_member_updated(filters.group, group=69)
async def member_has_joined(c: Alita, member: ChatMemberUpdated):
    from alita import BOT_ID

    if (
        member.new_chat_member
        and member.new_chat_member.status not in {"kicked", "left", "restricted"}
        and not member.old_chat_member
    ):
        pass
    else:
        return

    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    db = Greetings(member.chat.id)
    banned_users = gdb.check_gban(user.id)
    try:
        if user.id == BOT_ID:
            return
        if user.id == OWNER_ID:
            await c.send_message(
                member.chat.id,
                "❤Məryəm❤ Botun Sahibi Qrupa Qoşuldu Xoş Gəldin Sahibim🤗!",
            )
            return
        if banned_users:
            await member.chat.kick_member(user.id)
            await c.send_message(
                member.chat.id,
                f"{user.mention} was globally banned so i banned!",
            )
            return
        if user.is_bot:
            return  # ignore bots
    except ChatAdminRequired:
        return
    status = db.get_welcome_status()
    oo = db.get_welcome_text()
    parse_words = [
        "first",
        "last",
        "fullname",
        "username",
        "mention",
        "id",
        "chatname",
    ]
    hmm = await escape_mentions_using_curly_brackets_wl(member, True, oo, parse_words)
    if status:
        tek, button = await parse_button(hmm)
        button = await build_keyboard(button)
        button = InlineKeyboardMarkup(button) if button else None

        if "%%%" in tekss:
            filter_reply = tek.split("%%%")
            teks = choice(filter_reply)
        else:
            teks = tek
        ifff = db.get_current_cleanwelcome_id()
        gg = db.get_current_cleanwelcome_settings()
        if ifff and gg:
            try:
                await c.delete_messages(member.chat.id, int(ifff))
            except RPCError:
                pass
        try:
            jj = await c.send_message(
                member.chat.id,
                text=teks,
                reply_markup=button,
                disable_web_page_preview=True,
            )
            if jj:
                db.set_cleanwlcm_id(int(jj.message_id))
        except RPCError as e:
            print(e)
            return
    else:
        return


@Alita.on_chat_member_updated(filters.group, group=99)
async def member_has_left(c: Alita, member: ChatMemberUpdated):
    from alita import BOT_ID

    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {"kicked", "restricted"}
        and member.old_chat_member
    ):
        pass
    else:
        return
    db = Greetings(member.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    parse_words = [
        "first",
        "last",
        "fullname",
        "id",
        "username",
        "mention",
        "chatname",
    ]

    user = member.old_chat_member.user if member.old_chat_member else member.from_user

    hmm = await escape_mentions_using_curly_brackets_wl(member, False, oo, parse_words)
    if status:
        tek, button = await parse_button(hmm)
        button = await build_keyboard(button)
        button = InlineKeyboardMarkup(button) if button else None

        if "%%%" in tek:
            filter_reply = tek.split("%%%")
            teks = choice(filter_reply)
        else:
            teks = tek
        ifff = db.get_current_cleangoodbye_id()
        iii = db.get_current_cleangoodbye_settings()
        if ifff and iii:
            try:
                await c.delete_messages(member.chat.id, int(ifff))
            except RPCError:
                pass
        if user.id == OWNER_ID:
            await c.send_message(
                member.chat.id,
                "Sənin üçün darıxacam Sahibim🥺:)",
            )
            return
        try:
            ooo = await c.send_message(
                member.chat.id,
                text=teks,
                reply_markup=button,
                disable_web_page_preview=True,
            )
            if ooo:
                db.set_cleangoodbye_id(int(ooo.message_id))
            return
        except RPCError as e:
            print(e)
            return
    else:
        return


@Alita.on_message(command("welcome") & admin_filter)
async def welcome(c: Alita, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_welcome_status()
    oo = db.get_welcome_text()
    args = m.text.split(" ", 1)

    if m and not m.from_user:
        return

    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current welcome settings:-
        Welcome power: {status}
        Clean Welcome: {db.get_current_cleanwelcome_settings()}
        Cleaning service: {db.get_current_cleanservice_settings()}
        Welcome text in no formating:
        """,
            )
            await c.send_message(m.chat.id, text=oo, parse_mode=None)
            return
        if args[1].lower() == "on":
            db.set_current_welcome_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_welcome_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    else:
        await m.reply_text(
            f"""Current welcome settings:-
Welcome power: {status}
Clean Welcome: {db.get_current_cleanwelcome_settings()}
Cleaning service: {db.get_current_cleanservice_settings()}
Welcome text:
""",
        )
        tek, button = await parse_button(oo)
        button = await build_keyboard(button)
        button = InlineKeyboardMarkup(button) if button else None
        await c.send_message(m.chat.id, text=tek, reply_markup=button)
        return


@Alita.on_message(command("goodbye") & admin_filter)
async def goodbye(c: Alita, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    args = m.text.split(" ", 1)
    if m and not m.from_user:
        return
    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current goodbye settings:-
        Goodbye power: {status}
        Clean Goodbye: {db.get_current_cleangoodbye_settings()}
        Cleaning service: {db.get_current_cleanservice_settings()}
        Goodbye text in no formating:
        """,
            )
            await c.send_message(m.chat.id, text=oo, parse_mode=None)
            return
        if args[1].lower() == "on":
            db.set_current_goodbye_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_goodbye_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    else:
        await m.reply_text(
            f"""Current Goodbye settings:-
Goodbye power: {status}
Clean Goodbye: {db.get_current_cleangoodbye_settings()}
Cleaning service: {db.get_current_cleanservice_settings()}
Goodbye text:
""",
        )
        tek, button = await parse_button(oo)
        button = await build_keyboard(button)
        button = InlineKeyboardMarkup(button) if button else None
        await c.send_message(m.chat.id, text=tek, reply_markup=button)
        return


__PLUGIN__ = "greetings"
__alt_name__ = ["welcome", "goodbye", "cleanservice"]
