# bot.py
import os

import discord
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
client = discord.Client(command_prefix='!', intents=intents)

openai_client = OpenAI()
openai_client.api_key = os.getenv('OPENAI_API_KEY')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "!story":
        response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": "You are a parent telling the user a story. Tell the user an engaging story."}
        ]
        )

        await message.channel.send(response.choices[0].message.content)

client.run(TOKEN)