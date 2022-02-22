# STACBot

A bot for STAC's Discord server. It can do the following :
1. `@STACBot help`: replies with this help message.
2. `@STACBot ping`: Measure the delay for the bot to receive messages.
3. `@STACBot react [n:int,1+]`: Reacts to *n*th message in history with '🤩', '🔥', '👍', '💯'. Default value of n is 1.
4. `@STACBot poll <n:int,1+>`: starts a poll by reacting to n last messages with '👍' and '👎'.
5. `@STACBot events [month:1..12] [year:2002+]`: Get a list of astronomical events happening this month, or in the past
6. `@STACBot (image|photo) [k:int,0+]` : Display an astronomy-related photo of the day (for today, or *k* days ago); **or**; <br/>
   `@STACBot (image|photo) search <subject> [ show <n:1..10> ]` Display upto n (default 1) images of an astronomical object. 

This bot automatically reacts with '🤩', '🔥', '👍', '💯' to attached images and if there is a link in a message.
It also posts the upcoming events on the first day of each month in the dedicated channel. 
A limited number of recent messages are also cached in RAM to make it faster and avoid unnecessary network requests.


#### Steps to start using this
1. Make a discord bot using https://discord.com/developers.
2. Clone this repository.
3. make virtual environment by using `python3 -m virtualenv venv` in this directory.
4. activate venv using `source venv/bin/activate`. You are now in your virtual environment.
5. Install requirements using `pip3 install -r requierments.txt`.
6. Export all the required environment variables or save them to a `.env` file at the repo root.
7. Run the bot using `python3 bot.py`.
8. Hurrey! :partying_face:  Your bot is working. Send a help message to your bot, like `@MY_BOT_NAME help`.


#### Sources
- Astronomical event data is sourced from the calendars at skymaps.com/articles.
- Photographs displayed are from Astrobin's API. This bot is not endorsed or certified by AstroBin.
- Details of the exact article/photo are mentioned in the messages.
