# bot.py
import os
import re
import datetime
import asyncio
import logging
import logging.handlers
from dotenv import load_dotenv
import signal

import astroevents

import discord


load_dotenv()
filelog = logging.handlers.RotatingFileHandler('/var/log/bot/debug.log', 
                                                maxBytes=1024*1024, backupCount=9)
filelog.setLevel(logging.DEBUG)
stdlog = logging.StreamHandler()
stdlog.setLevel(logging.INFO)
logging.basicConfig(format='%(module)-12s %(levelname)-8s [%(asctime)s] %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[filelog, stdlog],
                    level=logging.DEBUG)

basepath = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(basepath,'.PID'), 'w') as _pidrecord:
    _pidrecord.write(str(os.getpid()))
logging.warning(f"Info : Started with PID {os.getpid()}")


TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ID = os.getenv('BOT_ID')

# client = discord.Client(connector=aiohttp.TCPConnector(local_addr=('0.0.0.0',5545)))
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
    logging.info(f'{client.user.name} has connected to Discord!')

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
    logging.debug(f'emojiList = {emojiList}')
    logging.debug(f'message = {message}')
    for emoji in emojiList:
        await message.add_reaction(emoji)
    logging.info('React emoji function finished')


@client.event
async def on_message(message):
    global prefix
    if message.author == client.user:
        return
    logging.info(f"Received message {message.id} in channel '{message.channel.name}'" +\
                 f" from {message.author.name}#{message.author.discriminator}")
    content = message.content.split()
    logging.debug(f'Message content: {content}')
    logging.debug(f'Attachments: {message.attachments}')
    try:
        if message.attachments:
            await react(fourEmojis, message)
            return
    except:
        logging.debug('There are no attachments in message.')
    try:
        if re.search(r"https?:\/\/[-a-z0-9@:%._+~#=]{1,256}\.[a-z0-9()]{1,6}\b([-a-z0-9()@:%_+.~#?&/=]*)",
            message.content, re.IGNORECASE) :
            await react(fourEmojis, message)
            return
    except:
        logging.error('URL not found in message.', exc_info=True)


    if checkMention(message):
        logging.info('Bot was mentioned, working on the task.')
    else:
        return

    try:
        if len(content)>1 and message.content.split()[1] == 'help':
            logging.info("sending help message")
            await message.channel.send('''
            Following Commands are allowed:
            1. `@{STACBot} help`: replies with this help message.
            2. `@{STACBot} react [n:int,1+]`: Reacts to <n>th message in history with '🤩', '🔥', '👍', '💯'. Default value of n is 1.
            3. `@{STACBot} poll <n:int,1+>`: starts a poll by reacting to n last messages with '👍' and '👎'.
            4. `@{STACBot} events [month:1..12] [year:2002+]`: Get a list of astronomical events happening this month, or in the past
            5. `@{STACBot} (picture|photo) [k:int,0+]` : Display an astronomy-related photo of the day.
            This bot automatically reacts with '🤩', '🔥', '👍', '💯' to attached images and if there is a link in a message.
            It also posts the upcoming events on the first day of each month in the dedicated channel.
            '''.format(STACBot=message.guild.me.display_name))
            return
    except:
        logging.error('This was not help command.', exc_info=True)
    try:
        if 'react' in content:
            if len(content) == 2:
                history = await message.channel.history(limit = 2).flatten()
                await react(fourEmojis, history[-1])
                await message.delete()
            elif len(content) == 3:
                if (content[-1][-2:] == 'th') or (content[-1][-2:] == 'st') or (content[-1][-2:] == 'nd') or (content[-1][-2:] == 'rd'):
                    index = int(content[-1][:-2])
                else :
                    index = int(content[-1])
                history = await message.channel.history(limit=index + 1).flatten()
                await react(fourEmojis, history[-1])
                await message.delete()
            return
    except:
        logging.error("\'react\' is not in message.", exc_info=True)

    try:
        if len(content)>1 and content[1] == 'poll':
            if not (len(content)>=3 and content[-1].isdigit()):
                await message.channel.send("Please specify number of messages to react to", reference=message)
                return
            limit = int(content[-1])
            messages = await message.channel.history(limit=limit + 1).flatten()
            logging.info("Executing Poll command")
            for msg in messages[1:]:
                await react(['👍', '👎'], msg)
            await message.delete()
            return
    except:
        logging.error("This was not a poll command.", exc_info=True)

    try :
        if len(content)>1 and content[1] == 'events':
            logging.info("Executing events command")
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
                (len(content)==5 and content[-1]=='withphoto'))
            embed = discord.Embed.from_dict(embdata)
            logging.info(f"Embed length {len(embed)}")
            await message.channel.send(embed=embed)
            return
    except:
        logging.error("Events command failed", exc_info=True)
    
    try :
        if len(content)>1 and (content[1]=='picture' or content[1]=='photo') :
            logging.info("Executing image of the day command")
            if len(content)>2 and content[2].isdigit() and int(content[2])>=0:
                offset = int(content[2])
                offstr = (datetime.date.today()-datetime.timedelta(days=offset)).strftime(' for %d/%m/%Y')
            else :
                offset, offstr = 0, ""
            imgdata = await astroevents.picoftheday(offset)
            url = imgdata.get('url_hd') or imgdata.get('url_regular', '')
            embed = discord.Embed.from_dict({
                'title':imgdata.get('title','Unknown'),
                'description':"Image of the Day" + offstr,
                'url':url,
                'image': {'url':url, 'height':imgdata.get('h'), 'width':imgdata.get('w')},
                'footer': {'text':"astrobin.com/{hash}, taken by {author}".format(
                    hash=imgdata.get('hash'), author=imgdata.get('user')
                )}
            })
            await message.channel.send(embed=embed)
            return
    except :
        logging.error("Image command failed", exc_info=True)

    # Bot was mentioned directly but none of the above commands matched
    try :
        await message.channel.send("Use `@{STACbot} help` to see what I can do !".format(
            STACbot=message.guild.me.display_name), reference=message) # send as reply
    except :
        logging.error('', exc_info=True)



async def loop_monthly():
    await client.wait_until_ready()
    channel = client.get_channel(id=int(os.getenv("EVENT_CHANNEL_ID")))
    logging.info(f"Beginning astro eventloop")
    if not client.is_closed():
        try :
            imgdata, embdata = await astroevents.fetch_and_parse()
            logging.debug(imgdata)
            logging.debug(embdata)
            embed = discord.Embed.from_dict(embdata)
            logging.info(f"Embed length {len(embed)}")
            await channel.send(embed=embed)
        except :
            logging.error("Astro event error\n", exc_info=True)
        logging.info("Astro eventloop done")
    else :
        logging.warning("Discord client was closed during astroevent call")


def loopevent_trigger(*args):
    global client
    logging.info(f"Received signal {args}")
    client.loop.create_task(loop_monthly())

signal.signal(signal.SIGUSR1, loopevent_trigger)

client.run(TOKEN)
