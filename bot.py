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

# Define the available models
models = {
    "model1": {
        "name": "Kandinsky",
        "model_id": "ai-forever/kandinsky-2.2",  # Replace with the actual model ID
        "version_id": "ea1addaab376f4dc227f5368bbd8eff901820fd1cc14ed8cad63b29249e9d463",  # Replace with the actual version ID
    },
    "model2": {
        "name": "StabilitySDXL",
        "model_id": "stability-ai/sdxl",  # Replace with the actual model ID
        "version_id": "d830ba5dabf8090ec0db6c10fc862c6eb1c929e1a194a5411852d25fd954ac82",  # Replace with the actual version ID
    },
}

async def generate_image(prompt, model):
    try:
        model_info = models.get(model)
        if model_info is None:
            return None

        model_id = model_info["model_id"]
        version_id = model_info["version_id"]

        model = replicate.models.get(model_id)
        version = model.versions.get(version_id)
        image = version.predict(prompt=prompt)[0]
        return image
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@bot.command(aliases=["g"])
async def generate(ctx, model, *, prompt):
    try:
        # Check if the user has the 'send_messages' permission
        if not ctx.channel.permissions_for(ctx.author).send_messages:
            await ctx.send("You do not have permission to send messages in this channel.")
            return

        # Convert the model name to lowercase to make it case-insensitive
        model = model.lower()

        # Check if the model name is valid
        if model not in models:
            await ctx.send("Invalid model name. Available models: model1, model2")
            return

        msg = await ctx.send(f"Using {models[model]['name']} for “{prompt}”\n> Generating...")

        image_task = asyncio.create_task(generate_image(prompt, model))
        image_url = await image_task

        if image_url is None:
            await ctx.send("An error occurred while generating the image.")
            return

        # Download the image from the URL
        response = requests.get(image_url)
        image_data = io.BytesIO(response.content)

        # Send the image as an attachment
        file = discord.File(image_data, f"{prompt}.png")
        await ctx.send(file=file)

        # Delete the "Generating..." message
        await msg.delete()

    except Exception as e:
        print(f"Error handling command: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command()
async def invite(ctx):
    """Get the invite link for the bot"""
    # Replace 'YOUR_CLIENT_ID' with your bot's actual client ID
    client_id = "1102551484941480037"
    permissions = "2147863554"
    
    # Construct the OAuth2 URL
    oauth_url = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"
    
    await ctx.send(f"Invite me to your server using this link: {oauth_url}")

@bot.command()
async def bot_help(ctx):
    """Display help and instructions for using the bot"""
    help_message = (
        "Welcome to the Kento Bot Help Screen!\n\n"
        "To generate an image, use the `!g` command followed by the model name and your text prompt.\n"
        "Available models:\n"
        "1. Kandinsky (Crystal Clear Reality Images) - model1\n"
        "2. Stability SDXL (Imaginative Images) - model2\n\n"
        "Example: `!g model1 a beautiful sunset image`\n\n"
        "To invite the bot to your server, use the `!invite` command.\n\n"
        "For more information and updates, visit the bot's website."
    )
    
    await ctx.send(help_message)

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