
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from markdownify import markdownify
from dotenv import load_dotenv
import datetime
import functools
import itertools
import logging
import re
import os
import sys

load_dotenv()

# Define values
COLOURLIST = ['000075','4363d8','42d4f4','469990','3cb44b','bfef45',
              'ffe119','f58231','e6194B','f032e6','911eb4','dcbeff']
CALENDAR_URL = "https://skymaps.com/articles/n{yy:02}{mm:02}.html"
IOTD_URL1 = "https://www.astrobin.com/api/v1/imageoftheday/?limit=1&api_key={key}&api_secret={secret}&format=json"
IOTD_URL2 = "https://www.astrobin.com{path}/?api_key={key}&api_secret={secret}&format=json"


def convertz(match,yy=None,mm=None,d=None,sub=True):
    if len(match.groups())==2:
        h, m = match.groups()
    else :
        h, m = match.groups()[0], 0
    h,m = map(int, (h,m))
    if type(d) != int : d = 1 # Placeholder, won't matter in this case
    offset = datetime.timedelta(hours=5.5)
    t0 = datetime.datetime(yy, mm, d, h, m) + offset
    if sub :
        return f"{t0.hour:02}:{t0.minute:02}"
    else :
        return (t0.month, t0.day)


async def picoftheday():
    global IOTD_URL1, IOTD_URL2

    try :
        # Add a picture of the day from astrobin.com
        logging.info("Beginning IOTD api request 1")
        async with aiohttp.ClientSession() as session:
            async with session.get(IOTD_URL1.format(key=os.getenv('PHOTO_API_KEY'), 
                                                    secret=os.getenv('PHOTO_API_SECRET'))) as resp1:
                resp1.raise_for_status() # Ensure valid HTTP response
                iotd_info = await resp1.json()

        logging.info("Beginning IOTD api request 2")
        async with aiohttp.ClientSession() as session:
            async with session.get(IOTD_URL2.format(path=iotd_info['objects'][0]['image'], 
                                                    key=os.getenv('PHOTO_API_KEY'), 
                                                    secret=os.getenv('PHOTO_API_SECRET'))) as resp2 :
                resp2.raise_for_status()
                iotd_imagedetails = await resp2.json()
    except :
        logging.error('IOTD request error', exc_info=True)
        return {}
    else :
        logging.info('IOTD request success')
        return iotd_imagedetails



async def fetch_and_parse(dt=None, with_photo=True):

    global COLOURLIST, CALENDAR_URL
    DTNOW = dt or datetime.date.today()
    YEAR, MONTH = DTNOW.year, DTNOW.month

    try :
        # Get this month's events from skymaps.com
        logging.info(f"Getting {CALENDAR_URL.format(yy=YEAR%100, mm=MONTH)}")
        async with aiohttp.ClientSession() as session:
            async with session.get(CALENDAR_URL.format(yy=YEAR%100, mm=MONTH)) as response :
                response.raise_for_status()
                web_result = await response.text()
                web_location = str(response.url)
    except :
        logging.error('Skymaps request error', exc_info=True)
    else :
        logging.info(f"Received {CALENDAR_URL.format(yy=YEAR%100, mm=MONTH)}!")


    # Extract useful HTML, parse into markdown, convert timezones to custom value
    bs = BeautifulSoup(web_result, features="html.parser")
    events = {}
    try :
        for tr in bs.select("table table")[0]("tr"):
            if len(tr('td')) != 2:
                continue
            try :
                DATE = int(next(tr.td.font.stripped_strings))
            except (ValueError, StopIteration):
                continue
            desc = ''.join(map(str, tr("td")[1].font.contents)).strip()
            neat = re.sub(r'\n+\s*\n*', '\n', markdownify(desc)).strip()

            r1 = re.compile(r'\b([012]?[0-9])\:([0-5][0-9])\b')
            r2 = re.compile(r'\b([012]?[0-9])h\b')
            months, dates = [], []
            # Does changing timezone shift the event into a diff date or month entirely ?
            for match in itertools.chain(re.finditer(r1, neat), re.finditer(r2, neat)):
                mo, dat = convertz(match, YEAR, MONTH, DATE, False)
                dates.append(dat); months.append(mo)
            if not any([m==MONTH for m in months]) : # Keep the event, but include month name with date
                DATE = datetime.date(YEAR, months[0], dates[0]).strftime('%b %d')
            elif not any([d==DATE for d in dates]) : # Shifted into neighbouring day
                DATE = dates[0]
            # Important to substitute r1 first, then r2
            neat = re.sub(r1, functools.partial(convertz, yy=YEAR,mm=MONTH,d=DATE,sub=True), neat)
            neat = re.sub(r2, functools.partial(convertz, yy=YEAR,mm=MONTH,d=DATE,sub=True), neat)
            neat = re.sub(r'\bUT\b', 'IST', neat)

            if DATE not in events :
                events[DATE] = []
            events[DATE].append(neat)
    except :
        logging.error('HTML parsing error', exc_info=True)
        logging.debug(bs)
    else :
        logging.info(f"Parsed {len(events)} event fields")


    # Discord Webhook API format
    embed = {
        "title": DTNOW.strftime("%B %Y"),
        "description": "Stargazing Events & Opportunities this month",
        "url": web_location,
        "color": int(COLOURLIST[MONTH-1],16),
        "fields": [
            {
                'name' : f'\n\n> *{name}*', 
                'value': '\n'.join(vals)
            } for name, vals in events.items()
        ],
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "footer":{
            "text":web_location.replace('https://','')
        }
    }

    # Add the picture to the message
    if with_photo :
        try :
            imgdata = await picoftheday()
            embed["image"] = {
                "url" : imgdata.get('url_regular',''),
                "height": imgdata.get('h',''),
                "width": imgdata.get('w','')
            }
            embed["footer"]["text"] += "\nPicture of the Day from astrobin.com by "+imgdata.get('user','')
        except :
            imgdata = {}
            logging.error("ERROR", exc_info=True)
    else :
        imgdata = {}

    return (imgdata, embed)

