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
import sys
from os import environ

import mariadb
DB_HOST = environ["MARIADB_HOST"]
DB_PORT = int(environ["MARIADB_PORT"])
DB_PASSWORD = environ["MARIADB_PASSWORD"]

try:
    conn = mariadb.connect(
        user="eznotes",
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database="eznotes"
    )
    conn.auto_reconnect = True
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS private_notes (
    user_id bigint UNSIGNED NOT NULL,
    date bigint UNSIGNED NOT NULL,
    share_count int NOT NULL DEFAULT 0,
    note_text text CHARACTER SET 'utf8mb4' NOT NULL,
    UNIQUE (user_id, date),
    FULLTEXT(note_text)
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS group_notes (
    chat_id bigint SIGNED NOT NULL,
    hashtag text NOT NULL,
    description text CHARACTER SET 'utf8mb4' NULL,
    note_text text CHARACTER SET 'utf8mb4' NOT NULL,
    UNIQUE (chat_id, hashtag)
)""")

conn.commit()
