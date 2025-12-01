import os
import random
import discord

COUNTING_CHANNEL_ID = 1444772755395580087

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

current_count = 0


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
    global current_count
    if message.author == bot.user:
        return
    if message.channel.id == COUNTING_CHANNEL_ID:
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
                rainbow_hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]
                for emoji in rainbow_hearts:
                    await message.add_reaction(emoji)
            else:
                current_count = 0
                await message.add_reaction("❌")
                await message.channel.send(
                    f"{message.author.mention} messed up at {n}. Start at 1."
                )
        except ValueError:
            pass


bot.run(os.environ["TOKEN"])
