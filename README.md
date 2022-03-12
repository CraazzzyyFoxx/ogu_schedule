## Schedule OGU

Bot that runs on Telegram.

## Running

Nevertheless, the installation steps are as follows:

1. **Make sure to get Python 3.10 or higher**

This is required to actually run the bot.

2. **Set up venv**

Just do `python3.10 -m venv venv`

3. **Install dependencies**

This is `pip install -U -r requirements.txt`

4. **Create the database in Sqlite3**

5. **Setup configuration**

The next step is just to create a `.env` file in the root directory where
the bot is with the following template:

```env
BOT_TOKEN=<bot_token_here>
SQLITE_DB=<file name with database>
```
