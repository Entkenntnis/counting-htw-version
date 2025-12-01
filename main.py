import discord
import os
from discord.ext import commands

# ---------------- CONFIGURATION ---------------- #
TOKEN = os.environ["TOKEN"]
COUNTING_CHANNEL_ID = 1444772755395580087  # Replace with the ID of your channel
# ----------------------------------------------- #

# Setup the bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read the numbers in messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Variable to track the current count
current_count = 0


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Ready to count in channel ID: {COUNTING_CHANNEL_ID}")


@bot.event
async def on_message(message):
    global current_count

    # 1. Ignore messages from the bot itself so it doesn't loop
    if message.author == bot.user:
        return

    # 2. Check if the message is in the specific counting channel
    if message.channel.id == COUNTING_CHANNEL_ID:

        # Try to convert the message text to a number
        try:
            if message.content.startswith("0b"):
                new_str = message.content.replace('0b', '')
                user_number = int(new_str, 2)
            user_number = int(message.content)

            # CHECK: Is the number correct? (Previous count + 1)
            if user_number == current_count + 1:
                current_count += 1
                await message.add_reaction("✅")

            # WRONG NUMBER LOGIC
            else:
                current_count = 0  # Reset count to 0
                await message.add_reaction("❌")
                await message.channel.send(
                    f"**WRONG!** {message.author.mention} messed up the count at {user_number}. Starting back at 1."
                )

        except ValueError:
            # This happens if the user sends text (like "hello") instead of a number.
            # You can choose to ignore it, or reset the count.
            # Usually, counting channels ignore chat text, so we pass.
            pass

    # This line is needed so other bot commands (if you add any) still work
    await bot.process_commands(message)


# Run the bot
bot.run(TOKEN)
