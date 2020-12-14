# bot.py
import os

import discord

# bot's stuff

TOKEN = os.getenv('DISCORD_TOKEN')
id = os.getenv('DISCORD_ID')
client = discord.Client()
GUILD = client.get_guild(id)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

client.run(TOKEN)
