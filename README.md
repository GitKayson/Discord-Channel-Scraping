# Discord Channel Monitor

A lightweight desktop application for monitoring multiple Discord text channels in real time through individual retro-styled terminal windows.

---

## Features

- Monitor up to 10 Discord channels simultaneously, each in its own window
- Retro terminal aesthetic built with a black and white Courier New style
- Loads the last 15 messages of history on connect for each channel
- Live message feed with author name, timestamp, and content
- Channel list is saved between sessions automatically
- Token is never stored by the app — supplied at launch each time

---

## Requirements

- Python 3.8 or higher
- A Discord bot token or your personal Discord account token
- Install dependencies with:

```
pip install -r requirements.txt
```

> **Linux users:** If tkinter is not included with your Python install, run:
> ```
> sudo apt install python3-tk
> ```

---

## Token Options

There are two ways to get a token to use with this app.

### Option 1 — Personal User Token

You can use your own Discord account token. The monitor will run as your account and can see every channel you already have access to no bot setup, no invites, no extra permissions needed.

To find your personal token:

1. Open Discord in your **browser**
2. Press `F12` to open DevTools and go to the **Network** tab
3. Send any message or perform any action in Discord
4. Find a network request that contains an `Authorization` header — the value is your token

> ⚠️ **Important:** Using a self-bot (personal token automation) is against Discord's Terms of Service. Only use this on your own account, for personal use, and never share your token with anyone Treat it  like a password.

---

### Option 2 — Bot Token

If you'd prefer to use a dedicated bot account:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and navigate to the **Bot** tab
3. Click **Reset Token** to generate your token — copy it somewhere safe
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Invite the bot to your server with at minimum the **Read Messages** and **Read Message History** permissions

---

## Getting Channel IDs

1. Open Discord and go to **Settings → Advanced**
2. Enable **Developer Mode**
3. Right-click any text channel and select **Copy Channel ID**

---

## Usage

Run the launcher:

```
python discord_launcher.py
```

On the setup screen:

1. Enter your token (personal or bot) in the token field
2. Add channels using their ID and a display name
3. Click **Start Monitoring**

A separate window will open for each channel and begin displaying live messages.

### Token shortcut options

To skip typing your token each launch, you can either:
- Set a `DISCORD_TOKEN` environment variable, or
- Place your token as plain text in a file named `token.txt` in the same folder as the script

---

## File Overview

| File | Description |
|---|---|
| `discord_launcher.py` | Main application — launcher GUI and Discord client |
| `discord_monitor_config.json` | Auto-generated file that saves your channel list |
| `requirements.txt` | Python dependencies |
| `token.txt` *(optional)* | Plain text file to store your token locally |

---

## Notes

- The monitor will only display messages from channels the token has access to
- Messages longer than 60 characters are truncated in the monitor window
- The app does not send any messages — it is read-only
- Keep your token private and never commit it to version control

---

## License

This project is provided as-is for personal use.
