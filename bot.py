import os
import asyncio
import replicate
import discord
import io
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def generate_image(prompt):
    model = replicate.models.get("stability-ai/stable-diffusion")
    version = model.versions.get("db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf")
    image = version.predict(prompt=prompt)[0]
    return image

@bot.command(aliases=["g"])
async def stable_diffusion(ctx, *, prompt):
    """Generate an image from a text prompt using the stable-diffusion model"""
    msg = await ctx.send(f"“{prompt}”\n> Generating...")

    image_task = asyncio.create_task(generate_image(prompt))
    image_url = await image_task

    # Download the image from the URL
    response = requests.get(image_url)
    image_data = io.BytesIO(response.content)

    # Send the image as an attachment
    file = discord.File(image_data, f"{prompt}.png")
    await ctx.send(file=file)

    # Delete the "Generating..." message
    await msg.delete()

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Received message: {message.content}")
    await bot.process_commands(message)

print("Starting the bot...")
bot.run(os.environ["DISCORD_TOKEN"])
