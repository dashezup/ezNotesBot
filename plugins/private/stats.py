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

from data import cur

DB_QUERY = """\
(SELECT
    CAST(COUNT(DISTINCT user_id) AS CHAR),
    CAST(COUNT(ALL user_id) AS CHAR) FROM private_notes
)
UNION ALL
(SELECT
    CAST(COUNT(DISTINCT chat_id) AS CHAR),
    CAST(COUNT(ALL chat_id) AS CHAR) FROM group_notes
)"""


@Client.on_message(filters.private
                   & filters.text
                   & filters.incoming
                   & ~filters.edited
                   & filters.regex('^/stats$'))
async def command_stats(_, m: Message):
    cur.execute(DB_QUERY)
    db_results = cur.fetchall()
    (users, private_notes), (groups, group_notes) = [
        [int(x) for x in i]
        for i in db_results
    ]
    # Python 3.8: f-string debugging
    await m.reply_text(
        f"{emoji.BAR_CHART} **Database Statistics for @ezNotesBot**:\n\n"
        f"\u2022 {users = }\n"
        f"\u2022 {private_notes = }\n"
        f"\u2022 {groups = }\n"
        f"\u2022 {group_notes = }"
    )
