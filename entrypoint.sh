#!/usr/bin/bash

# WORKDIR will be /usr/bot

# Setup crontab 
# IMPORTANT, rewrite the file instead of appending to avoid duplicating 
# lines in case container exits then is restarted with `docker start`
echo '
0 0 1 * * root kill -s USR1 $(cat /usr/bot/.PID)                                # Monthly bot post
*/10 * * * * root { cat /usr/bot/.PID; printf " | "; date; } >> /var/log/cron.log  # Verify that cron is up
' > /etc/cron.d/cron-tasks

# Environment variables
if [ ! -r .env ] ; then 
    echo "***** WARNING *****
No /usr/bot/.env file is present. \
The bot will not run unless the required variables have been set manually."
fi

# Start background tasks
cron
# Run the main program
python bot.py
