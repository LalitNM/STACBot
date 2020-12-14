# bot.py
import os
import random

import discord

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'roll a dice;':
        response = random.choice(range(1, 7))
        await message.channel.send(response)
    if 'addEmoji;' in message.content:
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')


client.run(TOKEN)
