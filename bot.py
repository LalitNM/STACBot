# bot.py
import os
import random

import discord

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

customEmojis = ['asteroid:788060704011845662', 'earth:788060705764540426', 'jupiter:788060702291656725', 'mars:788060701284499517', 'mercury:788060703315460106', 'moon:788060703235637268', 'neptune:788060701776019456', 'pluto:788060700739239967', 'saturn:788060701893460021', 'sun:788060705483915284', 'uranus:788060705102102610', 'venus:788060699694727178']
selectedEmojis = ['👍', '👎', '🔥', '🌟', '🤩', '👨‍🚀', '👩‍🚀', '👽', '🥳', '✨']
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if (message.content == "listemojis"):
        emojiList = list(message.guild.emojis);
        message.channel.send(emojiList.join());
    if message.content == 'roll a dice;':
        response = random.choice(range(1, 7))
        await message.channel.send(response)
    if 'addEmoji;' in message.content:
        for emoji in customEmojis + selectedEmojis:
            try:
                await message.add_reaction(emoji)
            except:
                print('Can\'t react with {}'.format(emoji))


client.run(TOKEN)
