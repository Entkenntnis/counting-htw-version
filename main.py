import os
import random
import discord

COUNTING_CHANNEL_ID = 1444772755395580087


rainbow_hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


current_count = 0
game_started = False  # Wird erst true wenn _anna_42_ "Start" schreibt


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
    global current_count, game_started
    if message.author == bot.user:
        return
    if message.channel.id == COUNTING_CHANNEL_ID:
        # Spielstart prüfen
        if not game_started:
            if message.content.strip().lower() == "start":
                game_started = True
                await message.channel.send("Na endlich. Spiel läuft. Fangt bei 1 an.")
                return
            else:
                # Reagiere nur knapp, ohne Spam von vielen Emojis
                await message.add_reaction("⏳")
                await message.channel.send(
                    "Tippe 'Start' um ein neues Spiel zu beginnen."
                )
                return
        try:
            if message.content.startswith("0b"):
                new_str = message.content.replace("0b", "")
                n = int(new_str, 2)
            elif message.content.startswith("0x"):
                new_str = message.content.replace("0x", "")
                n = int(new_str, 16)
            elif message.content.startswith("0o"):
                new_str = message.content.replace("0o", "")
                n = int(new_str, 8)
            else:
                n = int(message.content)

            if n == current_count + 1:
                current_count += 1
                # Reagiere mit allen Regenbogen-Herzen und zusätzlichem Regenbogen
                for emoji in rainbow_hearts:
                    await message.add_reaction(emoji)
            else:
                previous = current_count  # Wert vor Reset sichern
                # NOPE als Buchstaben-Reaktionen (Regional Indicator)
                nope = ["🇳", "🇴", "🇵", "🇪"]
                for emoji in nope:
                    await message.add_reaction(emoji)
                await message.channel.send(
                    f"{message.author.mention} Erwartet: {previous + 1}, falscher Wert geliefert ({n})."
                )
                await message.channel.send(
                    "Das Spiel ist vorbei. Danke fürs Mitspielen! Nächstes Mal besser!"
                )
                # add big cry emoji
                await message.channel.send("😭")
                current_count = 0
                game_started = False
        except ValueError:
            pass


bot.run(os.environ["TOKEN"])
