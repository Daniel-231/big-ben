import os
import discord
from discord.ext import commands, tasks
import asyncio
from dotenv import load_dotenv
import random
from datetime import datetime

# Load environment variables (for token)
load_dotenv()
token = os.getenv('TOKEN')

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Array of audio files to play during the day
audioFileArray = ["resources/sound-effect-1.mp3", "resources/sound-effect-2.mp3", "resources/sound-effect-2.mp3"]

# Specify the audio file to play at midnight
midnight_audio_file = "resources/strike-12.mp3"
fnafEasterEgg = "resources/five-nights-at-freddys-6-am.mp3"
oNanosEasterEgg = "resources/onanos.mp3"

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    join_voice_channel_at_target_time.start()  # Start the scheduled task

async def play_audio(voice_client, file_path):
    """Play an audio file in the specified voice client connection."""
    audio_source = discord.FFmpegPCMAudio(file_path)
    voice_client.play(audio_source)

    # Wait until the audio finishes playing
    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()  # Disconnect after playing

@tasks.loop(seconds=60)
async def join_voice_channel_at_target_time():
    now = datetime.now().strftime("%H:%M")

    # Determine which audio file to play at specific times
    if now == "00:00":
        file_to_play = midnight_audio_file  # Play the designated midnight file
    elif now.endswith(":00"):
        file_to_play = random.choice(audioFileArray)  # Play a random file every hour
    elif now.endswith("6:00"):
        file_to_play = fnafEasterEgg
    elif now.endswith("3:00"):
        file_to_play = oNanosEasterEgg
    else:
        print(f"Current time is {now}. Waiting for the next hour...")
        return  # Exit the function if it's not on the hour

    # Find the voice channel with the most members
    guild = bot.guilds[0]  # Modify if needed to specify a particular guild
    most_populated_channel = None
    max_members = 0
    for channel in guild.voice_channels:
        if len(channel.members) > max_members:
            most_populated_channel = channel
            max_members = len(channel.members)

    # Connect to the most populated voice channel and play the chosen audio file
    if most_populated_channel and max_members > 0:
        if not any(vc.channel == most_populated_channel for vc in bot.voice_clients):
            voice_client = await most_populated_channel.connect()
            await play_audio(voice_client, file_to_play)
            print(f"Playing audio in {most_populated_channel.name} with {max_members} members at {now}.")
        else:
            print(f"Bot is already in {most_populated_channel.name}.")
    else:
        print("No populated voice channels found.")

@bot.command()
async def leave(ctx):
    """Leave the current voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

# Run the bot with your token
bot.run(token)
