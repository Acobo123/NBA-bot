import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = 78aef0d4-780d-4848-a6fb-00a10b13db61
TELEGRAM_TOKEN = 8655761892:AAGykWvq_OqhegDgEloKntAsE4qPVxaH-oo

games_to_watch = []
alerts_sent = set()

# Guardar juegos
async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = " ".join(context.args)
    games_to_watch.append(game.lower())
    await update.message.reply_text(f"Agregado: {game}")

# Ver juegos guardados
async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Juegos: {games_to_watch}")

# Obtener juegos en vivo
def get_live_games():
    url = "https://api.balldontlie.io/v1/games"
    headers = {"Authorization": API_KEY}
    params = {"live": "true"}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("data", [])

# Checar condiciones
async def check_games(app):
    while True:
        try:
            games = get_live_games()

            for g in games:
                home = g["home_team"]["name"].lower()
                visitor = g["visitor_team"]["name"].lower()
                game_name = f"{home} vs {visitor}"

                if any(team in game_name for team in games_to_watch):
                    
                    home_score = g["home_team_score"]
                    visitor_score = g["visitor_team_score"]
                    period = g["period"]

                    diff = home_score - visitor_score

                    game_id = g["id"]

                    if (
                        diff >= 12
                        and period <= 2
                        and game_id not in alerts_sent
                    ):
                        alerts_sent.add(game_id)

                        message = f"""
🚨 ALERTA NBA

{g['home_team']['name']} (local)
+{diff} vs {g['visitor_team']['name']}
Q{period}

🔥 Dominando
"""
                        await app.bot.send_message(chat_id=CHAT_ID, text=message)

        except Exception as e:
            print(e)

        time.sleep(30)

# Iniciar bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot activo 🔥")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("seguir", seguir))
app.add_handler(CommandHandler("lista", lista))

# IMPORTANTE: pon tu chat_id aquí
CHAT_ID = "TU_CHAT_ID"

import asyncio
asyncio.create_task(check_games(app))

app.run_polling()
