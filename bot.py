import os
import random
import asyncio
import aiofiles
import discord

from openai import OpenAI
from dotenv import load_dotenv
from discord import FFmpegPCMAudio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

openai_client = OpenAI()
openai_client.api_key = os.getenv('OPENAI_API_KEY')

voices_list = ["alloy", "onyx", "echo", "fable", "nova", "shimmer"]

def create_pdf(story_text, filename="story.pdf"):
    pdf_path = f"./{filename}"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    y_position = 750
    for line in story_text.split("\n"):
        c.drawString(50, y_position, line)
        y_position -= 20

        if y_position < 50: 
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750

    c.save()
    return pdf_path

async def generate_story():
    """Generates a story using OpenAI."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Tell an engaging short story as if you're a parent telling it to a child."}]
    )
    return response.choices[0].message.content.strip()

async def generate_audio(text, filename="story_audio.mp3"):
    """Generates speech from text and saves it as an MP3 file asynchronously."""
    selected_voice = random.choice(voices_list)

    try:
        speech_response = await asyncio.to_thread(
            openai_client.audio.speech.create,
            model="tts-1",
            voice=selected_voice,
            input=text
        )

        async with aiofiles.open(filename, "wb") as audio_file:
            for chunk in speech_response.iter_bytes():
                await audio_file.write(chunk)

        print(f"Audio saved as {filename}")
        return filename

    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == "!storyaudio":
        await message.channel.send("Generating a story and saving it as a MP3...")

        story_text = await generate_story()
        audio_file = await generate_audio(story_text)

        await message.channel.send("Here’s your narrated story!", file=discord.File(audio_file))

    if message.content == "!storypdf":
        await message.channel.send("Generating a story and saving it as a PDF...")

        story_text = await generate_story()

        pdf_filename = f"{message.author.name}_story.pdf"
        pdf_path = create_pdf(story_text, pdf_filename)

        await message.channel.send(file=discord.File(pdf_path))

        os.remove(pdf_path)

    if message.content == "!join":
        if not message.author.voice:
            await message.channel.send(f"{message.author.name}, you need to be in a voice channel.")
            return
        
        channel = message.author.voice.channel
        await channel.connect()
        await message.channel.send("Joined the voice channel! 🎤")

    if message.content == "!leave":
        voice_client = message.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await message.channel.send("Disconnected from the voice channel.")
        else:
            await message.channel.send("I'm not in a voice channel.")

    if message.content == "!storyvoiceaudio":
        voice_client = message.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            await message.channel.send("I need to be in a voice channel! Use `!join` first.")
            return

        await message.channel.send("Generating your story... 🎙️")
        
        story_text = await generate_story()
        audio_file = await generate_audio(story_text)

        if not os.path.exists(audio_file):
            await message.channel.send("Error: Audio file was not generated.")
            return

        if voice_client.is_playing():
            voice_client.stop()

        audio_source = FFmpegPCMAudio(audio_file)
        voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))

        while voice_client.is_playing():
            await asyncio.sleep(1)

        try:
            os.remove(audio_file)
            print("Temporary audio file deleted.")
        except Exception as e:
            print(f"Error deleting file: {e}")

        await message.channel.send("Story narration finished! 🎧")


client.run(TOKEN)
