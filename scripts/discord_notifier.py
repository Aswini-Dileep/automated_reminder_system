import os
import asyncio
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import discord
from dotenv import load_dotenv

# ============================================================
# Load environment variables
# ============================================================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
DB_PATH = os.getenv("DB_PATH")

if not TOKEN or not CHANNEL_ID or not DB_PATH:
    raise ValueError("❌ Missing DISCORD_TOKEN, DISCORD_CHANNEL_ID, or DB_PATH in .env")

# ============================================================
# Discord bot setup
# ============================================================
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# ============================================================
# Helper: Track sent reminders
# ============================================================
SENT_LOG_PATH = "sent_reminders.log"

def load_sent_log():
    if os.path.exists(SENT_LOG_PATH):
        with open(SENT_LOG_PATH, "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_sent_log(sent_set):
    with open(SENT_LOG_PATH, "w") as f:
        for key in sent_set:
            f.write(key + "\n")

sent_reminders = load_sent_log()

# ============================================================
# Database helper functions
# ============================================================
def get_upcoming_classes():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM classes", conn)
    conn.close()
    return df

def get_upcoming_assignments():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM assignments", conn)
    conn.close()
    return df

async def send_reminder(channel, message):
    """Send a message to Discord channel."""
    try:
        await channel.send(message)
        print(f"✅ Sent: {message}")
    except Exception as e:
        print(f"⚠️ Failed to send message: {e}")

# ============================================================
# Reminder Logic
# ============================================================
async def check_and_send_reminders():
    """Checks database and sends reminders automatically every minute."""
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Could not find channel. Check your DISCORD_CHANNEL_ID.")
        return

    print("🔁 Reminder loop started...")

    while not bot.is_closed():
        now = datetime.now()

        # --- CLASSES ---
        df_classes = get_upcoming_classes()
        if not df_classes.empty:
            for _, row in df_classes.iterrows():
                try:
                    class_date = str(row["date"])
                    class_time = str(row["time"])
                    class_course = row["course"]
                    batch = row.get("batch_name", "")
                    class_name = row["session_name"]

                    class_datetime = datetime.strptime(
                        f"{class_date} {class_time}", "%Y-%m-%d %H:%M"
                    )

                    # Generate unique keys
                    key_24hr = f"class-{class_course}-{batch}-{class_name}-{class_date}-24hr"
                    key_1hr = f"class-{class_course}-{batch}-{class_name}-{class_date}-1hr"

                    seconds_until = (class_datetime - now).total_seconds()

                    # 📅 24 hours before reminder (within 10 min window)
                    if (
                        0 <= (seconds_until - 86400) <= 600
                        and key_24hr not in sent_reminders
                    ):
                        msg = (
                            f"📅 Heads-up! Tomorrow at **{class_time}**, your class "
                            f"**'{class_name}'** ({class_course} {batch}) will start. Be prepared! 🎓"
                        )
                        await send_reminder(channel, msg)
                        sent_reminders.add(key_24hr)

                    # ⚡ 1 hour before reminder (within 10 min window)
                    elif (
                        0 <= (seconds_until - 3600) <= 600
                        and key_1hr not in sent_reminders
                    ):
                        msg = (
                            f"⚡ Reminder: **'{class_name}'** ({class_course} {batch}) starts in 1 hour "
                            f"at **{class_time}**. Get ready! 🎒"
                        )
                        await send_reminder(channel, msg)
                        sent_reminders.add(key_1hr)

                except Exception as e:
                    print(f"⚠️ Error reading class data: {e}")

        # --- ASSIGNMENTS ---
        df_assignments = get_upcoming_assignments()
        if not df_assignments.empty:
            for _, row in df_assignments.iterrows():
                try:
                    due_date_str = str(row["due_date"])
                    if not due_date_str or due_date_str.lower() == "nan":
                        continue

                    subject = row["subject"]
                    course = row["course"]
                    batch = row.get("batch_name", "")
                    due_time = "23:59"  # Default

                    due_datetime = datetime.strptime(
                        f"{due_date_str} {due_time}", "%Y-%m-%d %H:%M"
                    )

                    key_24hr = f"assign-{course}-{batch}-{subject}-{due_date_str}-24hr"
                    key_1hr = f"assign-{course}-{batch}-{subject}-{due_date_str}-1hr"

                    seconds_until = (due_datetime - now).total_seconds()

                    # 🗓 24 hours before
                    if (
                        0 <= (seconds_until - 86400) <= 600
                        and key_24hr not in sent_reminders
                    ):
                        msg = (
                            f"📝 Reminder: Assignment **'{subject}'** ({course} {batch}) "
                            f"is due tomorrow at **{due_time}**! Don’t forget to submit! ⏰"
                        )
                        await send_reminder(channel, msg)
                        sent_reminders.add(key_24hr)

                    # ⏰ 1 hour before due
                    elif (
                        0 <= (seconds_until - 3600) <= 600
                        and key_1hr not in sent_reminders
                    ):
                        msg = (
                            f"⚠️ Assignment **'{subject}'** ({course} {batch}) is due in 1 hour "
                            f"at **{due_time}**! Submit it soon! 🕒"
                        )
                        await send_reminder(channel, msg)
                        sent_reminders.add(key_1hr)

                except Exception as e:
                    print(f"⚠️ Error reading assignment data: {e}")

        # Save sent reminders to file
        save_sent_log(sent_reminders)

        await asyncio.sleep(60)  # check every minute

# ============================================================
# Discord Events
# ============================================================
@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")

@bot.event
async def setup_hook():
    asyncio.create_task(check_and_send_reminders())

# ============================================================
# Run bot
# ============================================================
bot.run(TOKEN)
