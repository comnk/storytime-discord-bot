import os
import discord
from openai import OpenAI
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
client = discord.Client(command_prefix='!', intents=intents)

openai_client = OpenAI()
openai_client.api_key = os.getenv('OPENAI_API_KEY')

async def generate_story():
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Tell an engaging short story as if you're a parent telling it to a child."}
        ]
    )
    return response.choices[0].message.content

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

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "!story":
        await message.channel.send("HELLO!")

    if message.content == "!storypdf":
        await message.channel.send("Generating a story and saving it as a PDF...")

        story_text = await generate_story()

        pdf_filename = f"{message.author.name}_story.pdf"
        pdf_path = create_pdf(story_text, pdf_filename)

        await message.channel.send(file=discord.File(pdf_path))

        os.remove(pdf_path)

client.run(TOKEN)