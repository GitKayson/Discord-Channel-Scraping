import discord
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
import asyncio
import threading
import json
import os

# ---------------------------------------------------------------------------
# TOKEN LOADING
# Priority: 1) DISCORD_TOKEN environment variable  2) token.txt file  3) GUI prompt
# ---------------------------------------------------------------------------
CONFIG_FILE = "discord_monitor_config.json"


def load_token_from_file():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as f:
            return f.read().strip()
    return None


class RetroChannelWindow:
    def __init__(self, channel_id, channel_name, position):
        self.channel_id = channel_id
        self.window = tk.Toplevel()
        self.window.title(f"═══ {channel_name} ═══")
        self.window.geometry(f"400x350+{position[0]}+{position[1]}")
        self.window.configure(bg='black')

        # Retro-style header
        header = tk.Label(
            self.window,
            text=f"╔═══════════════════════════════════╗\n║  {channel_name.center(33)}  ║\n╚═══════════════════════════════════╝",
            bg='black',
            fg='white',
            font=('Courier New', 9, 'bold'),
            justify='left'
        )
        header.pack(pady=5)

        # Scrolled text area for messages
        self.text_area = scrolledtext.ScrolledText(
            self.window,
            bg='black',
            fg='white',
            font=('Courier New', 9),
            wrap=tk.WORD,
            insertbackground='white',
            state='disabled',
            relief='solid',
            borderwidth=2
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Status bar
        self.status = tk.Label(
            self.window,
            text="[CONNECTING...]",
            bg='black',
            fg='gray',
            font=('Courier New', 8),
            anchor='w'
        )
        self.status.pack(fill=tk.X, padx=10, pady=5)

    def add_message(self, text, is_system=False):
        self.text_area.config(state='normal')
        if is_system:
            self.text_area.insert(tk.END, f"{text}\n", 'system')
            self.text_area.tag_config('system', foreground='gray')
        else:
            self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

    def set_status(self, text):
        self.status.config(text=f"[{text}]")


class DiscordGUIMonitor(discord.Client):
    def __init__(self, channels):
        super().__init__()
        self.channel_config = channels
        self.windows = {}
        self.ready_event = asyncio.Event()

    def create_windows(self):
        for channel_id, info in self.channel_config.items():
            window = RetroChannelWindow(channel_id, info["name"], info["pos"])
            self.windows[channel_id] = window

    async def on_ready(self):
        print(f'Connected as {self.user.name}')

        for channel_id, window in self.windows.items():
            channel = self.get_channel(channel_id)
            if channel:
                window.add_message(f"╔═══════════════════════════════════╗", True)
                window.add_message(f"║ CHANNEL: #{channel.name.upper()}", True)
                window.add_message(f"║ SERVER: {channel.guild.name}", True)
                window.add_message(f"╚═══════════════════════════════════╝", True)
                window.add_message("", True)
                window.set_status("LOADING HISTORY...")

                # Load recent messages
                messages = []
                async for msg in channel.history(limit=15):
                    messages.append(msg)

                for msg in reversed(messages):
                    timestamp = msg.created_at.strftime('%I:%M%p')
                    author = msg.author.display_name[:15]
                    content = msg.content[:60] if msg.content else '[Image/File]'
                    window.add_message(f"[{timestamp}] {author}: {content}")

                window.add_message("", True)
                window.add_message("─" * 45, True)
                window.add_message("LIVE MONITORING ACTIVE", True)
                window.add_message("─" * 45, True)
                window.add_message("", True)
                window.set_status("CONNECTED - MONITORING")
            else:
                window.add_message(f"ERROR: Could not access channel", True)
                window.set_status("ERROR")

        self.ready_event.set()

    async def on_message(self, message):
        if message.channel.id in self.windows:
            window = self.windows[message.channel.id]

            if message.author.id == self.user.id:
                return

            timestamp = message.created_at.strftime('%I:%M%p')
            author = message.author.display_name[:15]

            content = message.content if message.content else ''
            if message.attachments:
                if content:
                    content += ' '
                content += '[Attachment]'
            if not content:
                content = '[Message]'

            # Truncate long messages
            if len(content) > 60:
                content = content[:57] + "..."

            window.add_message(f"[{timestamp}] {author}: {content}")


class LauncherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Discord Monitor - Channel Setup")
        self.root.geometry("500x680")
        self.root.configure(bg='black')

        # Load saved config
        self.channels = self.load_config()

        # Title
        title = tk.Label(
            self.root,
            text="╔═══════════════════════════════════════════╗\n║      DISCORD CHANNEL MONITOR SETUP       ║\n╚═══════════════════════════════════════════╝",
            bg='black',
            fg='white',
            font=('Courier New', 10, 'bold'),
            justify='left'
        )
        title.pack(pady=10)

        # ----- Token input -----
        token_frame = tk.Frame(self.root, bg='black')
        token_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        tk.Label(
            token_frame,
            text="Bot Token:",
            bg='black', fg='white',
            font=('Courier New', 9)
        ).pack(side=tk.LEFT, padx=5)

        self.token_entry = tk.Entry(
            token_frame,
            bg='black', fg='white',
            font=('Courier New', 9),
            insertbackground='white',
            relief='solid', borderwidth=1,
            show='*'          # hide token characters
        )
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Pre-fill token if found from env / file
        prefilled = os.environ.get("DISCORD_TOKEN") or load_token_from_file()
        if prefilled:
            self.token_entry.insert(0, prefilled)

        tk.Label(
            self.root,
            text="Tip: set DISCORD_TOKEN env var or place token in token.txt to skip this field.",
            bg='black', fg='#555555',
            font=('Courier New', 7),
            wraplength=460, justify='left'
        ).pack(padx=20, anchor='w')

        # ----- Instructions -----
        tk.Label(
            self.root,
            text="Add channel IDs to monitor (max 10 channels)",
            bg='black', fg='gray',
            font=('Courier New', 9)
        ).pack(pady=(8, 0))

        # Channel list frame
        list_frame = tk.Frame(self.root, bg='black')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollable channel list
        self.channel_listbox = tk.Listbox(
            list_frame,
            bg='black', fg='white',
            font=('Courier New', 9),
            selectmode=tk.SINGLE,
            relief='solid', borderwidth=2,
            selectbackground='white', selectforeground='black'
        )
        self.channel_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.channel_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.channel_listbox.config(yscrollcommand=scrollbar.set)

        # Populate list
        self.refresh_list()

        # Add channel frame
        add_frame = tk.Frame(self.root, bg='black')
        add_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(add_frame, text="Channel ID:", bg='black', fg='white', font=('Courier New', 9)).pack(side=tk.LEFT, padx=5)

        self.channel_id_entry = tk.Entry(
            add_frame,
            bg='black', fg='white',
            font=('Courier New', 9),
            insertbackground='white',
            relief='solid', borderwidth=1
        )
        self.channel_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Label(add_frame, text="Name:", bg='black', fg='white', font=('Courier New', 9)).pack(side=tk.LEFT, padx=5)

        self.channel_name_entry = tk.Entry(
            add_frame,
            bg='black', fg='white',
            font=('Courier New', 9),
            insertbackground='white',
            relief='solid', borderwidth=1,
            width=15
        )
        self.channel_name_entry.pack(side=tk.LEFT, padx=5)

        # Buttons frame
        button_frame = tk.Frame(self.root, bg='black')
        button_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(
            button_frame,
            text="ADD CHANNEL",
            bg='white', fg='black',
            font=('Courier New', 9, 'bold'),
            command=self.add_channel,
            relief='solid', borderwidth=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="REMOVE SELECTED",
            bg='white', fg='black',
            font=('Courier New', 9, 'bold'),
            command=self.remove_channel,
            relief='solid', borderwidth=2
        ).pack(side=tk.LEFT, padx=5)

        # Start button
        tk.Button(
            self.root,
            text="╔═══════════════════════╗\n║   START MONITORING   ║\n╚═══════════════════════╝",
            bg='white', fg='black',
            font=('Courier New', 10, 'bold'),
            command=self.start_monitoring,
            relief='solid', borderwidth=3
        ).pack(pady=20)

        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready to start",
            bg='black', fg='gray',
            font=('Courier New', 8)
        )
        self.status_label.pack(pady=5)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int
                    return {int(k): v for k, v in data.items()}
            except Exception:
                pass
        # Start with an empty channel list — users add their own
        return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.channels, f, indent=2)

    def refresh_list(self):
        self.channel_listbox.delete(0, tk.END)
        for channel_id, info in self.channels.items():
            self.channel_listbox.insert(tk.END, f"{info['name']}: {channel_id}")

    def add_channel(self):
        channel_id = self.channel_id_entry.get().strip()
        channel_name = self.channel_name_entry.get().strip()

        if not channel_id or not channel_name:
            messagebox.showerror("Error", "Please enter both Channel ID and Name")
            return

        try:
            channel_id = int(channel_id)
        except ValueError:
            messagebox.showerror("Error", "Channel ID must be a number")
            return

        if len(self.channels) >= 10:
            messagebox.showerror("Error", "Maximum 10 channels allowed")
            return

        # Calculate position
        idx = len(self.channels)
        row = idx // 3
        col = idx % 3
        pos = (50 + col * 300, 50 + row * 350)

        self.channels[channel_id] = {"name": channel_name, "pos": pos}
        self.save_config()
        self.refresh_list()

        self.channel_id_entry.delete(0, tk.END)
        self.channel_name_entry.delete(0, tk.END)

        self.status_label.config(text=f"Added {channel_name}")

    def remove_channel(self):
        selection = self.channel_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a channel to remove")
            return

        idx = selection[0]
        channel_id = list(self.channels.keys())[idx]
        channel_name = self.channels[channel_id]["name"]

        del self.channels[channel_id]
        self.save_config()
        self.refresh_list()

        self.status_label.config(text=f"Removed {channel_name}")

    def start_monitoring(self):
        if not self.channels:
            messagebox.showerror("Error", "Please add at least one channel")
            return

        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter your Discord bot token")
            return

        self.status_label.config(text="Starting monitor...")
        self.root.withdraw()

        # Create Discord client
        client = DiscordGUIMonitor(self.channels)
        client.create_windows()

        # Start Discord bot in separate thread
        def run_discord_bot():
            asyncio.set_event_loop(asyncio.new_event_loop())
            client.run(token)

        bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
        bot_thread.start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    launcher = LauncherGUI()
    launcher.run()
