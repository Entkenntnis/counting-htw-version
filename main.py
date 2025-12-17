import os
import random
import discord
import datetime
from parser import parse_message

COUNTING_CHANNEL_ID = 1444772755395580087


rainbow_hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


current_count = 0
game_started = False
cooldown_until = None
last_player_id = None
reaction_task = None
reaction_queue = None
last_count_message_id = None


async def _worker_reactions():
    # Single worker: processes newest jobs first, older jobs later
    global reaction_queue
    import asyncio

    while True:
        # Wait until there is something to do
        while reaction_queue and len(reaction_queue) > 0:
            message, emojis = reaction_queue.pop()  # LIFO: newest first (append/pop)
            try:
                for emoji in emojis:
                    await message.add_reaction(emoji)
            except Exception:
                # Ignore individual failures
                pass
        # Sleep briefly to yield control; prevents tight loop
        await asyncio.sleep(0.1)


def enqueue_reactions(message, emojis):
    """Enqueue reactions with priority: newest first, older still processed later."""
    global reaction_task, reaction_queue
    from collections import deque

    if reaction_queue is None:
        reaction_queue = deque()
    reaction_queue.append((message, emojis))
    if reaction_task is None or reaction_task.done():
        reaction_task = bot.loop.create_task(_worker_reactions())


async def end_game(message, text: str, cooldown: int):
    global current_count, game_started, cooldown_until, last_player_id, reaction_queue, reaction_task, last_count_message_id
    current_count = 0
    game_started = False
    cooldown_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=cooldown
    )
    last_player_id = None
    last_count_message_id = None
    # Empty any pending reaction jobs
    try:
        if reaction_queue is not None:
            reaction_queue.clear()
    except Exception:
        pass
    for emoji in ["🇳", "🇴", "🇵", "🇪"]:
        await message.add_reaction(emoji)
    await message.channel.send(text)
    await message.channel.send(
        f"Das Spiel ist vorbei. Danke fürs Mitspielen! Nächster Versuch in {cooldown} Minuten!"
    )
    await message.channel.send("😭")


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
    global current_count, game_started, cooldown_until, last_player_id, last_count_message_id
    if message.author == bot.user:
        return
    if message.channel.id == COUNTING_CHANNEL_ID:
        # Wenn Nachricht mit calc: beginnt, dann parse und Zeige das Ergebnis
        if message.content.strip().lower().startswith("calc:"):
            expr = message.content.strip()[5:].strip()
            n = parse_message(expr)
            if n is None:
                await message.channel.send(
                    f"{message.author.mention} Ungültiger Ausdruck."
                )
            else:
                n_rounded = round(n)
                if n != n_rounded:
                    await message.channel.send(
                        f"{message.author.mention} Das Ergebnis ist: `{n}` (gerundet: `{n_rounded}`)"
                    )
                else:
                    await message.channel.send(
                        f"{message.author.mention} Das Ergebnis ist: `{round(n)}`"
                    )
            return

        # Cooldown prüfen
        if cooldown_until is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if now < cooldown_until:
                if not message.content.strip().lower() == "start":
                    # Don't spam
                    return
                remaining = cooldown_until - now
                await message.add_reaction("⛔")
                remaining_seconds = round(remaining.total_seconds())
                if remaining_seconds > 3 * 60:
                    remaining_text = f"~{round(remaining_seconds / 60)} Minuten"
                else:
                    remaining_text = f"~{remaining_seconds}s"
                await message.channel.send(
                    f"Cooldown aktiv. Versuch's in {remaining_text} wieder"
                )
                return
            else:
                cooldown_until = None

        # Spielstart prüfen
        if not game_started:
            if message.content.strip().lower() == "start":
                game_started = True
                last_count_message_id = None
                await message.channel.send("Na endlich. Spiel läuft. Fangt bei 1 an.")
                return
            else:
                await message.add_reaction("⏳")
                await message.channel.send(
                    "Tippe 'Start' um ein neues Spiel zu beginnen."
                )
                return
        try:
            # Zahl parsen via separatem Parser
            n = parse_message(message.content)
            if n is None:
                return
            n = round(n)

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
                # Enqueue reactions with priority: latest number supersedes previous
                enqueue_reactions(message, rainbow_hearts)
                # Store the message id of the last valid count
                last_count_message_id = message.id
                # Merke den Spieler dieses korrekten Zugs
            else:
                await end_game(
                    message,
                    f"{message.author.mention} Wer zählen kann, ist klar im Vorteil. Erwartet: {current_count + 1}, geliefert: {n}.",
                    cooldown=max(2, current_count + 1),
                )
        except ValueError:
            pass


@bot.event
async def on_message_delete(message: discord.Message):
    # Only care about deletions in the counting channel
    try:
        if not message or not message.channel:
            return
        if message.channel.id != COUNTING_CHANNEL_ID:
            return
        # We compare against the last stored valid count message id
        global last_count_message_id, current_count
        if last_count_message_id is not None and message.id == last_count_message_id:
            warn = (
                f"⚠️ Die letzte gültige Zähl-Nachricht wurde gelöscht. "
                f"Zuletzt gezählter Wert: {current_count}."
            )
            await message.channel.send(warn)
    except Exception:
        # Never fail the bot because of debug notifications
        pass


bot.run(os.environ["TOKEN"])
