import random
import time
import sqlite3

from telegram import Update
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
ContextTypes
)

TOKEN = "8759811593:AAGYDGyRxKUttDcVpJhYypcnJPB-ZU24_d0"

=========================

اتصال به دیتابیس

=========================

db = sqlite3.connect(
"game.db",
check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
username TEXT PRIMARY KEY,
power INTEGER,
lost INTEGER,
gained INTEGER,
last_power INTEGER
)
""")

db.commit()

=========================

ساخت بازیکن

=========================

def create_player(username):

cursor.execute(
    "SELECT * FROM players WHERE username = ?",
    (username,)
)

player = cursor.fetchone()

if not player:

    cursor.execute(
        """
        INSERT INTO players
        (username, power, lost, gained, last_power)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, 100, 0, 0, 0)
    )

    db.commit()

=========================

گرفتن اطلاعات بازیکن

=========================

def get_player(username):

cursor.execute(
    "SELECT * FROM players WHERE username = ?",
    (username,)
)

return cursor.fetchone()

=========================

start

=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    "سلام به بات گیمینگ Manhunt 🎮\n"
    "خوش اومدی!\n"
    "برای راهنما /help رو بزن."
)

=========================

help

=========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    "/start = شروع ربات\n"
    "/help = نمایش این پیغام راهنما\n"
    "/fight = درخواست فایت\n"
    "/accept = تایید فایت\n"
    "/top = نمایش برترین شکارچی ها\n"
    "/power = افزایش قدرت برای شکار\n"
    "/me = نمایش اطلاعات خودتان\n"
    "/kod = نمایش کاربرد کد ها"
)

=========================

fight

=========================

async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):

user = update.effective_user

username = (
    f"@{user.username}"
    if user.username
    else user.first_name
)

create_player(username)

await update.message.reply_text(
    f"کاربر {username} شما را به چالش کشید 💪!!\n"
    "روی همین پیام ریپلای بزن و بنویس:\n"
    "/accept"
)

=========================

accept

=========================

async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not update.message.reply_to_message:

    await update.message.reply_text(
        "باید روی پیام /fight ریپلای بزنی!"
    )

    return

accepter = update.effective_user

accepter_name = (
    f"@{accepter.username}"
    if accepter.username
    else accepter.first_name
)

reply_user = update.message.reply_to_message.from_user

challenger_name = (
    f"@{reply_user.username}"
    if reply_user.username
    else reply_user.first_name
)

create_player(accepter_name)
create_player(challenger_name)

winner = random.choice([
    challenger_name,
    accepter_name
])

loser = (
    accepter_name
    if winner == challenger_name
    else challenger_name
)

loser_data = get_player(loser)

loser_power = loser_data[1]

new_power = loser_power - 10

if new_power < 0:
    new_power = 0

cursor.execute(
    """
    UPDATE players
    SET power = ?, lost = lost + 10
    WHERE username = ?
    """,
    (new_power, loser)
)

db.commit()

rate = random.randint(50, 100)

await update.message.reply_text(
    f"شکارچی انسان {winner} فینیشر بهتری پیاده کرد 🩸🪓\n"
    f"و کاربر {loser} شکست خورد 💀\n"
    f"نرخ برد : {rate}%\n\n"
    f"قدرت باقی‌مانده {loser}: {new_power}"
)

=========================

power

=========================

async def power(update: Update, context: ContextTypes.DEFAULT_TYPE):

user = update.effective_user

username = (
    f"@{user.username}"
    if user.username
    else user.first_name
)

create_player(username)

player = get_player(username)

power_amount = player[1]
last_power = player[4]

current_time = int(time.time())

# محدودیت 24 ساعت
if current_time - last_power < 86400:

    remain = 86400 - (
        current_time - last_power
    )

    hours = remain // 3600
    minutes = (remain % 3600) // 60

    await update.message.reply_text(
        f"⏳ {username}\n"
        f"{hours} ساعت و {minutes} دقیقه مانده."
    )

    return

# احتمال کم شدن قدرت
if power_amount > 50:

    if random.choice([True, False]):

        remove_power = random.randint(1, 20)

        new_power = power_amount - remove_power

        if new_power < 0:
            new_power = 0

        cursor.execute(
            """
            UPDATE players
            SET power = ?,
                lost = lost + ?,
                last_power = ?
            WHERE username = ?
            """,
            (
                new_power,
                remove_power,
                current_time,
                username
            )
        )

        db.commit()

        await update.message.reply_text(
            f"💀 {username}\n"
            f"{remove_power} قدرت از دست دادی!"
        )

        return

# افزایش قدرت
add_power = random.randint(1, 20)

new_power = power_amount + add_power

cursor.execute(
    """
    UPDATE players
    SET power = ?,
        gained = gained + ?,
        last_power = ?
    WHERE username = ?
    """,
    (
        new_power,
        add_power,
        current_time,
        username
    )
)

db.commit()

await update.message.reply_text(
    f"💪 {username}\n"
    f"{add_power} قدرت شکار گرفتی!"
)

=========================

top

=========================

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):

cursor.execute(
    """
    SELECT username, power
    FROM players
    ORDER BY power DESC
    """
)

players = cursor.fetchall()

if not players:

    await update.message.reply_text(
        "هیچ بازیکنی ثبت نشده 💀"
    )

    return

text = "🏆 برترین شکارچی‌ها:\n\n"

rank = 1

for player in players:

    text += (
        f"{rank}. {player[0]} | "
        f"{player[1]} 💪\n"
    )

    rank += 1

await update.message.reply_text(text)

=========================

me

=========================

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):

user = update.effective_user

username = (
    f"@{user.username}"
    if user.username
    else user.first_name
)

create_player(username)

player = get_player(username)

power_amount = player[1]
lost_amount = player[2]
gained_amount = player[3]

cursor.execute(
    """
    SELECT username
    FROM players
    ORDER BY power DESC
    """
)

ranking = cursor.fetchall()

rank = 1

for r in ranking:

    if r[0] == username:
        break

    rank += 1

await update.message.reply_text(
    f"🎮 اطلاعات شکارچی {username}\n\n"
    f"💪 قدرت فعلی: {power_amount}\n"
    f"💀 قدرت از دست رفته: {lost_amount}\n"
    f"🔥 قدرت گرفته: {gained_amount}\n"
    f"🏆 رتبه: {rank}"
)

=========================

kod

=========================

async def kod(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    "📖 کاربرد کد های بازی 👇\n\n"
    "/start\n"
    "/help\n"
    "/fight\n"
    "/accept\n"
    "/top\n"
    "/power\n"
    "/me\n"
    "/kod"
)

=========================

ساخت ربات

=========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
CommandHandler("start", start)
)

app.add_handler(
CommandHandler("help", help_command)
)

app.add_handler(
CommandHandler("fight", fight)
)

app.add_handler(
CommandHandler("accept", accept)
)

app.add_handler(
CommandHandler("power", power)
)

app.add_handler(
CommandHandler("top", top)
)

app.add_handler(
CommandHandler("me", me)
)

app.add_handler(
CommandHandler("kod", kod)
)

print("Bot Started...")

app.run_polling()