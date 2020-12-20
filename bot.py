# bot.py
import os
import random

import discord

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ID = os.getenv('BOT_ID')
client = discord.Client()
customEmojis = ['asteroid:788060704011845662', 'earth:788060705764540426', 'jupiter:788060702291656725', 'mars:788060701284499517', 'mercury:788060703315460106', 'moon:788060703235637268', 'neptune:788060701776019456', 'pluto:788060700739239967', 'saturn:788060701893460021', 'sun:788060705483915284', 'uranus:788060705102102610', 'venus:788060699694727178']
fourEmojis = ['🤩', '🔥', '👍', '💯']
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

def checkMention(message):
    '''Checks if the bot was mentioned, returns true or false accordingly.'''
    if ('<@' + str(BOT_ID) + '>') in message.content or ('<@!' + str(BOT_ID) + '>') in message.content:
        return True
    return False


async def react(emojiList, message):
    ''' input:
    1. emojiList - list of emojis with which bot should react
    2. message - the target message.
    output: replies to the message having index = messageIndex.
    '''
    global client, selectedEmojis, customEmojis, fourEmojis
    print('emojiList =', emojiList)
    print('message =', message)
    for emoji in emojiList:
        await message.add_reaction(emoji)
    print('React emoji function finished')

@client.event
async def on_message(message):
    global prefix
    if message.author == client.user:
        return
    print('Message Recieved\n\n', message, '\n\n')
    content = message.content.split()
    print('Message content\n\n', content, '\n\n')

    print('Attachments: ', message.attachments)
    try:
        if message.attachments:
            await react(fourEmojis, message)
            return
    except:
        print('There are no attachments in message.')
    try:
        if 'http' in message.content:
            await react(fourEmojis, message)
            return
    except:
        print('\'http\' not in message.')


    if checkMention(message):
        print('Bot was mentioned, working on the task.')
    else:
        return

    try:
        if message.content.split()[1] == 'help':
            await message.channel.send('''
            Following Commands are allowed:
            1. `@STACbot help`: replies with this help message.
            2. `@STACbot react <n>th`: Reacts to <n>th message in history with '🤩', '🔥', '👍', '💯'. Default value of n is 1.
            3. `@STACbot poll n`: starts a poll by reacting to n last messages with '👍' and '👎'.
            4. This bot reacts with '🤩', '🔥', '👍', '💯' to attached images and if there is a link in a message.
            ''')
    except:
        print('This was not help command.')
    try:
        if 'react' in content:
            if len(content) == 2:
                history = await message.channel.history(limit = 2).flatten()
                await react(fourEmojis, history[-1])
                await message.delete()
            elif len(content) == 3:
                if (content[-1][-2:] == 'th') or (content[-1][-2:] == 'st') or (content[-1][-2:] == 'nd') or (content[-1][-2:] == 'rd'):
                    index = int(content[-1][:-2])
                    history = await message.channel.history(limit=index + 1).flatten()
                    await react(fourEmojis, history[-1])
                    await message.delete()

                await react([content[-1]], message)
            return
    except:
        print("\'react\' is not in message.")
    print(message.content)

    try:
        if content[1] == 'poll':
            limit = int(content[-1])
            messages = await message.channel.history(limit=limit + 1).flatten()
            print("Executing Poll command")
            for msg in messages[1:]:
                await react(['👍', '👎'], msg)
            await message.delete()
            return
    except:
        print("This was not a poll command.")


client.run(TOKEN)
