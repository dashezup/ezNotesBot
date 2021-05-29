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
import asyncio

from pyrogram import Client, filters, emoji
from pyrogram.types import (Message, CallbackQuery, ForceReply,
                            InlineKeyboardMarkup, InlineKeyboardButton)

from data import conn, cur

DELAY_DELETE = 6
ASK_TO_SEND_NOTE = "Write the text you want to add as a new note"
START_TEXT = (f"""{emoji.ROBOT} **Save and Share Personal and Group Notes**:

\u2022 inline mode and PM for private notes
\u2022 add the bot to groups to use hashtag based notes
\u2022 check `/help` for usage

[Source Code](https://github.com/dashezup/ezNotesBot) \
| [Developer](https://t.me/dashezup) \
| [Support Chat](https://t.me/ezupdev)""")
START_REPLY_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                f"{emoji.ROCKET} Share",
                switch_inline_query=""
            ),
            InlineKeyboardButton(
                f"{emoji.HAMMER_AND_WRENCH} Manage",
                switch_inline_query_current_chat="-"
            ),
            InlineKeyboardButton(
                f"{emoji.MAGNIFYING_GLASS_TILTED_LEFT} Search",
                switch_inline_query_current_chat=""
            )
        ],
        [
            InlineKeyboardButton(
                f"{emoji.PLUS} Add to a Group",
                url="https://t.me/ezNotesBot?startgroup="
            )
        ]
    ]
)


@Client.on_message(filters.private
                   & filters.text
                   & filters.incoming
                   & ~filters.edited
                   & filters.command('start'))
async def command_start(_, m: Message):
    command = m.command
    len_command = len(command)
    if len_command == 1:
        await m.reply_text(
            START_TEXT,
            reply_markup=START_REPLY_MARKUP,
            disable_web_page_preview=True
        )
    elif len_command == 2 and command[1] == "add_note":
        await m.reply_text(ASK_TO_SEND_NOTE, reply_markup=ForceReply())


@Client.on_message(filters.private
                   & filters.reply
                   & filters.text
                   & ~filters.edited
                   & ~filters.via_bot)
async def save_note(_, m: Message):
    cur.execute(
        "INSERT IGNORE INTO private_notes "
        "(user_id, date, note_text) VALUES (?, ?, ?)",
        (m.from_user.id, m.date, m.text.html)
    )
    conn.commit()
    m_reply = m.reply_to_message
    if m_reply.text == ASK_TO_SEND_NOTE:
        await m.reply_text(START_TEXT,
                           reply_markup=START_REPLY_MARKUP,
                           disable_web_page_preview=True)
        await m_reply.delete()
    else:
        m_response = await m.reply_text(
            f"{emoji.CHECK_MARK_BUTTON} Saved as a new note",
            quote=True
        )
        await _delay_delete_message(m_response)


@Client.on_callback_query(filters.regex("^start$"))
async def cq_start(_, cq: CallbackQuery):
    await cq.edit_message_text(START_TEXT, reply_markup=START_REPLY_MARKUP)
    await cq.answer(f"{emoji.ROBOT} Main Page")


async def _delay_delete_message(m: Message):
    await asyncio.sleep(DELAY_DELETE)
    await m.delete()
