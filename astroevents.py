
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from markdownify import markdownify
from dotenv import load_dotenv
import datetime
import traceback
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


def convertz(yy,mm,d,h,m):
    offset = datetime.timedelta(hours=5.5)
    t0 = datetime.datetime(yy, mm, d, h, m) + offset
    return (t0.month, t0.day, t0.hour, t0.minute)



async def picoftheday():
    global IOTD_URL1, IOTD_URL2

    # Add a picture of the day from astrobin.com
    print("Beginning IOTD api request 1")
    async with aiohttp.ClientSession() as session:
        async with session.get(IOTD_URL1.format(key=os.getenv('PHOTO_API_KEY'), 
                                                secret=os.getenv('PHOTO_API_SECRET'))) as resp1:
            resp1.raise_for_status() # Ensure valid HTTP response
            iotd_info = await resp1.json()

    print("Beginning IOTD api request 2")
    async with aiohttp.ClientSession() as session:
        async with session.get(IOTD_URL2.format(path=iotd_info['objects'][0]['image'], 
                                                key=os.getenv('PHOTO_API_KEY'), 
                                                secret=os.getenv('PHOTO_API_SECRET'))) as resp2 :
            resp2.raise_for_status()
            iotd_imagedetails = await resp2.json()

    return iotd_imagedetails
    # return {'url_regular': 'https://www.astrobin.com/qer3uo/0/rawthumb/regular/','h':300,'w':500,'user':'x'}




async def fetch_and_parse(dt=None, with_photo=True):

    # return (
    #     {'animated': False, 'bookmarks': 3, 'comments': 18, 'data_source': 'AMATEUR_HOSTING', 'dec': '-37.170', 'description': '', 'h': 1639, 'hash': 'yx76x9', 'id': 659781, 'imaging_cameras': ['FLI Proline 16803'], 'imaging_telescopes': ['Planewave 17" CDK'], 'is_final': False, 'is_solved': True, 'license': 0, 'license_name': 'ALL_RIGHTS_RESERVED', 'likes': 176, 'link': 'https://www.good-astronomy.com', 'link_to_fits': None, 'locations': [], 'orientation': '312.326', 'pixscale': '1.270', 'published': '2022-02-03T22:06:41.530320', 'ra': '50.655', 'radius': '0.419', 'remote_source': 'DSW', 'resource_uri': '/api/v1/image/659781/', 'revisions': [], 'solution_status': 'SUCCESS', 'subjects': ['Fornax A', 'Fornax B', 'NGC 1310', 'NGC 1316', 'NGC 1317'], 'title': 'NGC 1316', 'updated': '2022-02-14T05:52:03.630561', 'uploaded': '2022-01-29T13:15:31.667587', 'url_advanced_skyplot': None, 'url_advanced_skyplot_small': None, 'url_advanced_solution': None, 'url_duckduckgo': 'https://www.astrobin.com/yx76x9/0/rawthumb/duckduckgo/', 'url_duckduckgo_small': 'https://www.astrobin.com/yx76x9/0/rawthumb/duckduckgo_small/', 'url_gallery': 'https://www.astrobin.com/yx76x9/0/rawthumb/gallery/', 'url_hd': 'https://www.astrobin.com/yx76x9/0/rawthumb/hd/', 'url_histogram': 'https://www.astrobin.com/yx76x9/0/rawthumb/histogram/', 'url_real': 'https://www.astrobin.com/yx76x9/0/rawthumb/real/', 'url_regular': 'https://www.astrobin.com/yx76x9/0/rawthumb/regular/', 'url_skyplot': 'https://cdn.astrobin.com/images/skyplots/images/8588/2022/65bc5015-43bc-45b6-9679-050b2dc0bd2a.jpeg', 'url_solution': 'https://cdn.astrobin.com/solutions/images/8588/2022/65bc5015-43bc-45b6-9679-050b2dc0bd2a-1643469803.jpeg', 'url_thumb': 'https://www.astrobin.com/yx76x9/0/rawthumb/thumb/', 'user': 'crgood2', 'views': 462, 'w': 1716},
    #     {'title': 'February 2022', 'description': 'Stargazing Events & Opportunities this month', 'url': 'https://skymaps.com/articles/n2202.html', 'color': 4416472, 'fields': [{'name': '\n\n> *1*', 'value': '**New Moon** at 11:18 IST. Start of lunation 1226.\n**Moon near Mercury** at 04:30 IST (24° from Sun, morning sky). Mag. −0.1.\n• [Mercury](https://en.wikipedia.org/wiki/Mercury_(planet)) (Wikipedia)'}, {'name': '\n\n> *3*', 'value': '**Moon near Jupiter** at 06:30 IST (evening sky). Mag. −2.0.\n• [Jupiter](http://en.wikipedia.org/wiki/Jupiter) (Wikipedia)'}, {'name': '\n\n> *5*', 'value': '**Saturn at conjunction** with the Sun at 00:30 IST. The ringed planet (not visible) passes into the morning sky.\n• [Saturn](http://en.wikipedia.org/wiki/Saturn) (Wikipedia)\n**Mars 0.2° from M22** (globular star cluster) at 14:30 IST (38° from Sun, morning sky). Mags. 1.4 and 5.2.'}, {'name': '\n\n> *8*', 'value': '**Moon near Uranus** (82° from Sun, evening sky) at 02:30 IST. Occultation visible from Antarctica. Mag. +5.8.\n**First Quarter Moon** at 19:21 IST.'}, {'name': '\n\n> *9*', 'value': '**Moon near the Pleiades** at 17:30 IST (evening sky).\n• [The Pleiades](http://en.wikipedia.org/wiki/Pleiades) (Wikipedia)\n**Venus at its brightest** at 19:30 IST. Mag. −4.7.\n• [Venus](http://en.wikipedia.org/wiki/Venus) (Wikipedia)'}, {'name': '\n\n> *10*', 'value': '**Moon near Aldebaran** at 12:30 IST (evening sky).\n• [Aldebaran](http://en.wikipedia.org/wiki/Aldebaran) (Wikipedia)'}, {'name': '\n\n> *11*', 'value': "**Moon at apogee** (farthest from Earth) at 08:30 IST (distance 404,897 km; angular size 29.5')."}, {'name': '\n\n> *12*', 'value': '**Moon near M35 star cluste**r at 10:30 IST (evening sky).'}, {'name': '\n\n> *13*', 'value': '**Venus shows greatest illuminated extent** (337 square arc seconds) at 03:30 IST. Mag. −4.6\n**Moon near Castor** at 23:30 IST (evening sky).'}, {'name': '\n\n> *14*', 'value': '**Moon near Pollux** at 05:30 IST (evening sky).'}, {'name': '\n\n> *15*', 'value': '**Moon near Beehive cluster M44** at 08:30 IST (evening sky).\n• [Beehive Cluster](http://en.wikipedia.org/wiki/Messier_44) (Wikipedia)  \n• [M44: The Beehive Cluster](http://apod.nasa.gov/apod/ap140222.html) (APOD)'}, {'name': '\n\n> *16*', 'value': '**Full Moon** at 22:28 IST.'}, {'name': '\n\n> *17*', 'value': '**Mercury at greatest elongation west** at 02:30 IST (26° from Sun, morning sky). Mag. 0.0.\n**Moon near Regulus** at 03:30 IST (midnight sky).\n• [Regulus](http://en.wikipedia.org/wiki/Regulus) (Wikipedia)'}, {'name': '\n\n> *21*', 'value': '**Moon near Spica** at 05:30 IST (morning sky).\n• [Spica](http://en.wikipedia.org/wiki/Spica) (Wikipedia)'}, {'name': '\n\n> *24*', 'value': '**Last Quarter Moon** at 04:03 IST.\n**Moon near Antares** at 13:30 IST (morning sky).\n• [Antares](http://en.wikipedia.org/wiki/Antares) (Wikipedia)'}, {'name': '\n\n> *27*', 'value': "**Moon at perigee** (closest to Earth) at 04:09 IST (distance 367,789km; angular size 32.5').\n**Moon near Venus** at 12:30 IST (47° from Sun, morning sky). Mag. −4.6.\n• [Venus](http://en.wikipedia.org/wiki/Venus) (Wikipedia)\n**Moon near Mars** at 16:30 IST (44° from Sun, morning sky). Mag. 1.3.\n• [Mars](http://en.wikipedia.org/wiki/Mars) (Wikipedia)"}], 'timestamp': '2022-02-14T06:03:48.633218', 'footer': {'text': 'skymaps.com/articles/n2202.html\nPicture of the Day from astrobin.com by crgood2'}, 'image': {'url': 'https://www.astrobin.com/yx76x9/0/rawthumb/regular/', 'height': 1639, 'width': 1716}}
    # )

    global COLOURLIST, CALENDAR_URL
    DTNOW = dt or datetime.date.today()
    YEAR, MONTH = DTNOW.year, DTNOW.month

    # Get this month's events from skymaps.com
    print("Getting", CALENDAR_URL.format(yy=YEAR%100, mm=MONTH))
    async with aiohttp.ClientSession() as session:
        async with session.get(CALENDAR_URL.format(yy=YEAR%100, mm=MONTH)) as response :
            response.raise_for_status()
            web_result = await response.text()
            web_location = str(response.url)
    print(f"Received {CALENDAR_URL.format(yy=YEAR%100, mm=MONTH)}!")


    # Extract useful HTML, parse into markdown, convert timezones to custom value
    bs = BeautifulSoup(web_result, features="html.parser")
    events = {}
    for tr in bs.select("table table table")[0]("tr"):
        if len(tr('td')) != 2:
            continue
        try :
            date = int(next(tr.td.font.stripped_strings))
        except (ValueError, StopIteration):
            continue
        desc = ''.join(map(str, tr("td")[1].font.contents)).strip()
        neat = re.sub(r'\n+\s*\n*', '\n', markdownify(desc)).strip()

        r1 = re.search(r'([0-9]{1,2})\:([0-9]{1,2})\s+(UT)', neat)
        r2 = re.search(r'([0-9]{1,2})h\s+(UT)', neat)
        if r1 :
            h, m, ut = r1.groups()
            mo, date, h, m = convertz(YEAR, MONTH, date, int(h), int(m))
            neat = re.sub(r'([0-9]{1,2})\:([0-9]{1,2})\s+(UT)', f"{h:02}:{m:02} IST", neat)
        elif r2 :
            h, ut = r2.groups()
            mo, date, h, m = convertz(YEAR, MONTH, date, int(h), 0)
            neat = re.sub(r'([0-9]{1,2})h\s+(UT)', f"{h:02}:{m:02} IST", neat)

        if mo != MONTH :
            continue
        if date not in events :
            events[date] = []
        events[date].append(neat)
    print(f"Parsed {len(events)} event fields")


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
                "url" : imgdata['url_regular'],
                "height": imgdata['h'],
                "width": imgdata['w']
            }
            embed["footer"]["text"] += "\nPicture of the Day from astrobin.com by "+imgdata['user']
        except :
            imgdata = {}
            print("ERROR\n", traceback.format_exc())
    else :
        imgdata = {}

    return (imgdata, embed)




# if __name__ == '__main__':
#     # d = main()
#     print("Data", *d, sep='\n\n')
