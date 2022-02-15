# bot.py
import os
import random
import traceback
import datetime
import  asyncio
from dotenv import load_dotenv

import astroevents

import discord


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ID = os.getenv('BOT_ID')

client = discord.Client()

customEmojis = ['asteroid:788060704011845662', 'earth:788060705764540426', 
                'jupiter:788060702291656725', 'mars:788060701284499517', 
                'mercury:788060703315460106', 'moon:788060703235637268', 
                'neptune:788060701776019456', 'pluto:788060700739239967', 
                'saturn:788060701893460021', 'sun:788060705483915284', 
                'uranus:788060705102102610', 'venus:788060699694727178']
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
            1. `@{STACBot} help`: replies with this help message.
            2. `@{STACBot} react [n:int,1+]`: Reacts to <n>th message in history with '🤩', '🔥', '👍', '💯'. Default value of n is 1.
            3. `@{STACBot} poll <n:int,1+>`: starts a poll by reacting to n last messages with '👍' and '👎'.
            4. `@{STACBot} events [month:1..12] [year:2002+]`: Get a list of astronomical events happening this month, or in the past
            5. `@{STACBot} (picture|photo)` : Display an astronomy-related photo of the day.
            This bot automatically reacts with '🤩', '🔥', '👍', '💯' to attached images and if there is a link in a message.
            It also posts the upcoming events on the first day of each month in the dedicated channel.
            '''.format(STACBot=client.user.name))
            return
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
        print("\'react\' is not in message.\n", traceback.format_exc())
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
        print("This was not a poll command.\n", traceback.format_exc())

    try :
        if content[1] == 'events':
            print("Executing events command")
            dt = None
            if len(content) >= 3 and content[2].isdigit() :
                try :
                    if len(content) >= 4  and content[3].isdigit() :
                        dt = datetime.date(int(content[3]), int(content[2]), 1)
                    else :
                        dt = datetime.date(datetime.date.today().year, int(content[2]), 1)
                    if not datetime.date(2002,8,1) <= dt <= datetime.date.today() :
                        raise ValueError
                except ValueError :
                    await message.channel.send("Invalid date", reference=message)
                    return
            imgdata, embdata = await astroevents.fetch_and_parse(dt, 
                len(content)==4 and content[2:]==['with','photo'])
            embed = discord.Embed.from_dict(embdata)
            print("Embed length", len(embed))
            await message.channel.send(embed=embed)
            return
    except:
        print("Events command failed\n", traceback.format_exc())
    
    try :
        if content[1]=='picture' or content[1]=='photo' :
            print("Executing image of the day command")
            imgdata = await astroevents.picoftheday()
            url = imgdata.get('url_hd') or imgdata.get('url_regular', '')
            embed = discord.Embed.from_dict({
                'title':imgdata.get('title','Unknown'),
                'description':"Image of the Day",
                'url':url,
                'image': {'url':url, 'height':imgdata.get('h'), 'width':imgdata.get('w')},
                'footer': {'text':"astrobin.com/{hash}, taken by {author}".format(
                    hash=imgdata.get('hash'), author=imgdata.get('user')
                )}
            })
            await message.channel.send(embed=embed)
            return
    except :
        print("Image command failed\n", traceback.format_exc())

    # Bot was mentioned directly but none of the above commands matched
    try :
        await message.channel.send(f"Use `@{client.user.name} help` to see what I can do !", reference=message) # send as reply
    except :
        print(traceback.format_exc())



async def loop_monthly():
    await client.wait_until_ready()
    channel = client.get_channel(id=int(os.getenv("EVENT_CHANNEL_ID")))
    print("Beginning astro eventloop",str(datetime.datetime.now()))
    while not client.is_closed():
        # First day of the month
        dt = datetime.datetime.now()
        if dt.date == 1 :
            print("Event fetch fired",str(datetime.datetime.now()))
            try :
                imgdata, embdata = await astroevents.fetch_and_parse()
                print(imgdata, embdata, sep='\n\n', end='\n\n')
                embed = discord.Embed.from_dict(embdata)
                print("Embed length", len(embed))
                await channel.send(embed=embed)
            except :
                print("ERROR\n", traceback.format_exc())
        # Repeat every day
        await asyncio.sleep(60 * 60 * 24)
        print("Astro eventloop iteration",str(datetime.datetime.now()))


client.loop.create_task(loop_monthly())
client.run(TOKEN)
