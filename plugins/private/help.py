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
from pyrogram import Client, filters, emoji
from pyrogram.types import Message

HELP_TEXT = (f"""{emoji.PLUS} **Save Notes**:
\u2022 __reply to any message to save it as a new note__

{emoji.MAGNIFYING_GLASS_TILTED_LEFT} **Inline Search**:
\u2022 `[|text]` __show all notes or search \"text\" in your notes__
\u2022 `-` (hyphen-minus) __manage notes, most recently added at first__
\u2022 `#` (number sign) __list all notes, from oldest to newest__""")


@Client.on_message(filters.private
                   & filters.text
                   & filters.incoming
                   & ~filters.edited
                   & filters.regex('^/help$'))
async def command_help(_, m: Message):
    await m.reply_text(HELP_TEXT)
