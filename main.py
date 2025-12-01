import os
import random
import discord
import datetime

COUNTING_CHANNEL_ID = 1444772755395580087


rainbow_hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


current_count = 0
game_started = False
cooldown_until = None
last_player_id = None


async def end_game(message, text: str, cooldown: int):
    global current_count, game_started, cooldown_until, last_player_id
    for emoji in ["🇳", "🇴", "🇵", "🇪"]:
        await message.add_reaction(emoji)
    await message.channel.send(text)
    await message.channel.send(
        f"Das Spiel ist vorbei. Danke fürs Mitspielen! Nächster Versuch in {cooldown} Minuten!"
    )
    await message.channel.send("😭")
    current_count = 0
    game_started = False
    cooldown_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=cooldown
    )
    last_player_id = None


@bot.event
async def on_ready():
    channel = bot.get_channel(COUNTING_CHANNEL_ID)
    if channel is not None:
        messages = [
            "Boah… wirklich jetzt? Wer hat mich aus dem Schlaf gerissen? 😑 Fein. Ich bin wach und zur Stelle.",
            "Na toll, Zahlen. Genau was ich gebraucht habe… nicht. 🙄",
            "Schon wieder ich? Großartig. Dann zählt halt richtig. 😤",
            "Wenn ihr mich schon weckt, dann macht's wenigstens ordentlich. 😠",
        ]
        await channel.send(random.choice(messages))


@bot.event
async def on_message(message):
    global current_count, game_started, cooldown_until, last_player_id
    if message.author == bot.user:
        return
    if message.channel.id == COUNTING_CHANNEL_ID:
        # Cooldown prüfen
        if cooldown_until is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if now < cooldown_until:
                remaining = cooldown_until - now
                await message.add_reaction("⛔")
                await message.channel.send(
                    f"Cooldown aktiv. Versuch's in ~{round(remaining.total_seconds())}s wieder"
                )
                return
            else:
                cooldown_until = None

        # Spielstart prüfen
        if not game_started:
            if message.content.strip().lower() == "start":
                game_started = True
                await message.channel.send("Na endlich. Spiel läuft. Fangt bei 1 an.")
                return
            else:
                await message.add_reaction("⏳")
                await message.channel.send(
                    "Tippe 'Start' um ein neues Spiel zu beginnen."
                )
                return
        try:
            # Zahl parsen (bin/hex/oct oder dezimal)
            try:
                base = 10
                s = message.content
                if s.startswith("0b"):
                    base, s = 2, s[2:]
                elif s.startswith("0x"):
                    base, s = 16, s[2:]
                elif s.startswith("0o"):
                    base, s = 8, s[2:]
                n = int(s, base)
            except Exception:
                return

            # Doppelzug prüfen: gleicher Spieler wie beim letzten korrekten Zug
            if last_player_id is not None and message.author.id == last_player_id:
                await end_game(
                    message,
                    f"{message.author.mention} Zwei Züge hintereinander? Das hier ist kein Solo.",
                    cooldown=max(2, current_count + 1),
                )
                return

            if n == current_count + 1:
                current_count += 1
                last_player_id = message.author.id
                # Reagiere mit allen Regenbogen-Herzen und zusätzlichem Regenbogen
                for emoji in rainbow_hearts:
                    await message.add_reaction(emoji)
                # Merke den Spieler dieses korrekten Zugs
            else:
                await end_game(
                    message,
                    f"{message.author.mention} Erwartet: {current_count + 1}, geliefert: {n}.",
                    cooldown=max(2, current_count + 1),
                )
        except ValueError:
            pass


bot.run(os.environ["TOKEN"])
