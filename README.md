## EZ Notes Bot (ezNotesBot)

Telegram Bot for saving and sharing personal and group notes.

### Usage

**Personal notes**:

- reply to any message in PM to save it as a new note
- search in inline mode for sharing notes
- search `-` (hyphen-minus) for managing notes

**Group notes**:

- only anonymous admin can add/remove notes
- `+#hashtag [description]` (as a reply) to add/replace a note
- `-#hashtag` remove a note
- `/notes` list notes
- `#hashtag` show a note

### Setup

This bot uses MariaDB for saving notes

#### Requirements

- Python 3.8 or higher
- A [Telegram API key](https://docs.pyrogram.org/intro/setup#api-keys)
- A Telegram Bot created with [BotFather](https://t.me/BotFather) with
  "inline mode" and "inline feedback" enabled (for personal notes)
  and "group privacy mode" disabled (for group notes)
- `libmariadbclient`

**Mariadb**:

Shell

```
sudo mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
# start MariaDB service
```

SQL

```
-- sudo mysql -u root
DROP USER IF EXISTS eznotes;
DROP DATABASE IF EXISTS eznotes;
CREATE DATABASE eznotes;
GRANT CREATE,DELETE,INSERT,SELECT,UPDATE ON eznotes.* TO `eznotes`@`localhost` IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

#### Run the Bot

Create a new `config.ini`, copy-paste the following and replace the values with
your own

```
[pyrogram]
api_id = 1234567
api_hash = 0123456789abcdef0123456789abcdef
bot_token = 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

Run it

```
virtualenv venv
venv/bin/pip install -U -r requirements.txt
export MARIADB_HOST="localhost"
export MARIADB_PORT="3306"
export MARIADB_PASSWORD="password"
venv/bin/python bot.py
```

### License

AGPL-3.0-or-later

```
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
```