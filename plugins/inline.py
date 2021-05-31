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
from datetime import datetime

from pyrogram import Client, filters, emoji
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    ChosenInlineResult,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)

from data import conn, cur

SQL_ORDER_RULES = {
    '': 'share_count DESC',
    '-': 'date DESC',
    '#': 'date'
}

# https://www.vecteezy.com/vector-art/357052-vector-notes-icon
# https://emojipedia.org/memo/
THUMB_URL = (
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/"
    "thumbs/120/openmoji/272/memo_1f4dd.png"
)
NUM_ITEMS_PER_PAGE = 10


@Client.on_inline_query()
async def answer_iq(c: Client, iq: InlineQuery):
    query_text = iq.query
    offset = int(iq.offset or 0)
    if query_text in ('-', '#', ''):
        sql_query = (
            "SELECT date, share_count, note_text FROM private_notes "
            f"WHERE (user_id=?) ORDER BY {SQL_ORDER_RULES[query_text]} "
            "LIMIT ? OFFSET ?"
        )
        sql_data = (iq.from_user.id, NUM_ITEMS_PER_PAGE, offset)
    else:
        sql_query = ("SELECT date, share_count, note_text FROM private_notes "
                     "WHERE (user_id=? AND match(note_text) AGAINST(?)) "
                     "LIMIT ? OFFSET ?")
        sql_data = (iq.from_user.id, query_text, NUM_ITEMS_PER_PAGE, offset)
    cur.execute(sql_query, sql_data)
    db_results = cur.fetchall()
    iq_results = [
        InlineQueryResultArticle(
            title=f"{emoji.KEYCAP_NUMBER_SIGN} {offset + i + 1}  "
                  f"{emoji.FIRE if note[1] else emoji.STAR} {note[1]}  "
                  f"{emoji.CALENDAR} "
                  + (datetime.utcfromtimestamp(note[0])
                     .strftime('%F')),
            input_message_content=InputTextMessageContent(
                note[2],
                parse_mode='html',
                disable_web_page_preview=True),
            id=f"{iq.from_user.id}_{note[0]}",
            description=(await c.parser.parse(note[2], 'html'))['message']
            [:120],
            thumb_url=THUMB_URL,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{emoji.WASTEBASKET} Delete",
                            callback_data=f"delete_note_{note[0]}"
                        ),
                        InlineKeyboardButton(
                            f"{emoji.CROSS_MARK} Ignore",
                            callback_data="delete_buttons"
                        )
                    ]
                ]) if query_text == '-' else None
        )
        for i, note in enumerate(db_results)
    ]
    await iq.answer(
        iq_results,
        cache_time=1,
        next_offset=str(offset + NUM_ITEMS_PER_PAGE) if iq_results else '',
        switch_pm_text=f"{emoji.PLUS} Add a New Note {emoji.MEMO}",
        switch_pm_parameter="add_note"
    )


@Client.on_chosen_inline_result()
async def chosen_inline_result(_, cir: ChosenInlineResult):
    user_id, note_date = cir.result_id.split('_')
    cur.execute('UPDATE IGNORE private_notes '
                'SET share_count = share_count + 1 '
                'WHERE (user_id=? AND date=?)',
                (user_id, note_date))
    conn.commit()


@Client.on_callback_query(filters.regex('^delete_buttons$'))
async def delete_buttons(_, cq: CallbackQuery):
    await cq.edit_message_reply_markup(None)
    await cq.answer()


@Client.on_callback_query(filters.regex('^delete_note_\\d{0,10}$$'))
async def delete_note(_, cq: CallbackQuery):
    note_date = int(cq.data[12:])
    cur.execute("DELETE FROM private_notes WHERE (user_id=? AND date=?)",
                (cq.from_user.id, note_date))
    conn.commit()
    await cq.answer(
        f"{emoji.WASTEBASKET} Successfully deleted this note",
        show_alert=True
    )
    await cq.edit_message_reply_markup(None)
