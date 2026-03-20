import os
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

games_to_watch = set()
alerts_sent = set()


# 🔹 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot activo 🔥")


# 🔹 /seguir lakers
async def seguir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = " ".join(context.args).lower()
    games_to_watch.add(game)
    await update.message.reply_text(f"Agregado: {game}")


# 🔹 /lista
async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not games_to_watch:
        await update.message.reply_text("No estás siguiendo nada 👀")
    else:
        lista = "\n".join(games_to_watch)
        await update.message.reply_text(f"📋 Juegos:\n{lista}")


# 🔹 API async
async def get_live_games():
    url = "https://api.balldontlie.io/v1/games"
    headers = {"Authorization": API_KEY}
    params = {"live": "true"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            data = await resp.json()
            return data.get("data", [])


# 🔹 Lógica principal
async def monitor(context: ContextTypes.DEFAULT_TYPE):
    try:
        games = await get_live_games()

        for g in games:
            home = g["home_team"]["name"].lower()
            visitor = g["visitor_team"]["name"].lower()
            game_name = f"{home} vs {visitor}"

            if not any(team in game_name for team in games_to_watch):
                continue

            home_score = g["home_team_score"]
            visitor_score = g["visitor_team_score"]
            period = g["period"]
            game_id = g["id"]

            diff = abs(home_score - visitor_score)

            if home_score > visitor_score:
                leader = g["home_team"]["name"]
            else:
                leader = g["visitor_team"]["name"]

            # 🔥 CONDICIÓN
            if diff >= 12 and period <= 2 and game_id not in alerts_sent:
                alerts_sent.add(game_id)

                message = (
                    f"🚨 ALERTA NBA\n\n"
                    f"{leader} dominando\n"
                    f"Diferencia: {diff}\n"
                    f"Periodo: Q{period}\n\n"
                    f"{g['home_team']['name']} {home_score} - {visitor_score} {g['visitor_team']['name']}"
                )

                await context.bot.send_message(chat_id=int(CHAT_ID), text=message)

    except Exception as e:
        print("Error monitor:", e)


# 🔥 MAIN (YA CORRECTO)
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("seguir", seguir))
    app.add_handler(CommandHandler("lista", lista))

    app.job_queue.run_repeating(monitor, interval=30, first=5)

    print("Bot corriendo 🔥")
    app.run_polling()


if __name__ == "__main__":
    main()
