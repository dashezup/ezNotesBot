"""
ezNotesBot, Telegram Bot for saving and sharing personal and group notes
Copyright (C) 2021  Dash Eclipse

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import re
from typing import Optional

from pyrogram import Client, filters, emoji
from pyrogram.types import Message

from data import conn, cur

p = re.compile(
    r'^(\+|-|)'
    r'#([a-zA-Z0-9(_)]{2,})'
    r'( |)'
    r'(.*|)$',
    flags=re.UNICODE
)
_GROUP_HELP = (
    f"{emoji.HAMMER_AND_WRENCH} **Anonymous admin can add/remove notes**:\n"
    "\u2022 `+#hashtag [description]` (as a reply) __add/replace a note__\n"
    "\u2022 `-#hashtag` __remove a note__\n\n"
    f"{emoji.SPIRAL_NOTEPAD} "
    "**All members can get the list of notes or a specified note**:\n"
    "\u2022 `/notes` __list notes__\n"
    "\u2022 `#hashtag` __show a note__"
)
GROUP_HELP = (f"""\
{emoji.HAMMER_AND_WRENCH} **Anonymous admin can add/remove notes**:
\u2022 `+#hashtag [description]` (as a reply) __add/replace a note__
\u2022 `-#hashtag` __remove a note__

{emoji.SPIRAL_NOTEPAD} \
**All members can get the list of notes or a specified note**:
\u2022 `/notes` __list notes__
\u2022 `#hashtag` __show a note__""")

m_collection = {}


@Client.on_message(filters.group
                   & filters.incoming
                   & filters.text
                   & ~filters.edited
                   & filters.regex('^/help@ezNotesBot'))
async def show_help(_, m: Message):
    await m.reply_text(GROUP_HELP)


@Client.on_message(filters.group
                   & filters.incoming
                   & filters.text
                   & ~filters.edited)
async def hashtag_command(_, m: Message):
    if m.text in ('/notes', '/notes@ezNotesBot'):
        note_list = await db_list_notes(m.chat.id)
        m_response = await m.reply_text(note_list)
        await update_collection(m_response)
        return
    match_list = p.findall(m.text)
    if not match_list:
        return
    action, hashtag, _, description = p.findall(m.text)[0]
    m_reply = m.reply_to_message
    if not action:
        response = await db_show_note(m.chat.id, hashtag)
        if response:
            m_target = m_reply or m
            m_response = await m_target.reply_text(
                response,
                parse_mode='html',
                disable_web_page_preview=True
            )
            await update_collection(m_response)
        return
    if action and m.sender_chat and m.sender_chat.id == m.chat.id:
        if action == '+' and m_reply and m_reply:
            response = await db_add_note(m.chat.id, hashtag,
                                         description, m_reply.text.html)
            await m_reply.reply_text(response)
            return
        if action == '-':
            response = await db_remove_note(m.chat.id, hashtag)
            await m.reply_text(response)
            return


async def update_collection(m: Message):
    chat_id = m.chat.id
    m_old_response = m_collection.get(chat_id)
    try:
        if m_old_response.reply_to_message.text[:1] in ('/', '#'):
            await m_old_response.delete()
    except (AttributeError, TypeError):
        pass
    m_collection[chat_id] = m


async def db_add_note(chat_id, hashtag, description, text) -> str:
    sql_query = (
        "INSERT INTO group_notes "
        "(chat_id, hashtag, description, note_text) VALUES (?, ?, ?, ?) "
        "ON DUPLICATE KEY UPDATE "
        "description=VALUES(description), note_text=VALUES(note_text)"
    )
    sql_data = (chat_id, hashtag, description, text)
    cur.execute(sql_query, sql_data)
    conn.commit()
    return f"{emoji.CHECK_MARK_BUTTON} added note #{hashtag}"


async def db_remove_note(chat_id, hashtag) -> str:
    cur.execute("DELETE FROM group_notes WHERE (chat_id=? AND hashtag=?)",
                (chat_id, hashtag))
    conn.commit()
    return f"{emoji.CROSS_MARK_BUTTON} removed note #{hashtag}"


async def db_show_note(chat_id, hashtag) -> Optional[str]:
    sql_query = ("SELECT description, note_text FROM group_notes "
                 "WHERE (chat_id=? AND hashtag=?)")
    sql_data = (chat_id, hashtag)
    cur.execute(sql_query, sql_data)
    query_result = cur.fetchone()
    return (
        f"{emoji.LABEL} <b>{query_result[0]}</b> (/notes #{hashtag}):"
        f"\n\n{query_result[1]}"
        if query_result else None
    )


async def db_list_notes(chat_id) -> str:
    sql_query = (
        "SELECT hashtag, description FROM group_notes WHERE (chat_id=?)"
    )
    sql_data = (chat_id,)
    cur.execute(sql_query, sql_data)
    query_results = cur.fetchall()
    if query_results:
        note_list = [
            f"\u2022 `#{note[0]}` __{note[1]}__"
            for note in query_results
        ]
        content = "\n".join(note_list)
        response = f"{emoji.SPIRAL_NOTEPAD} **Notes** (/notes):\n\n{content}"
    else:
        response = "No notes for this chat yet"
    return response
