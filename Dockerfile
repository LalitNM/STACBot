FROM python:3.9

WORKDIR /usr/bot
ADD . .

RUN pip install --no-cache-dir -r requirements.txt

ADD crontab /etc/cron.d/cron-tasks
RUN chmod 0644 /etc/cron.d/cron-tasks
RUN apt-get update 
RUN apt-get -y install cron lsof less

# Files to store logs
RUN touch /var/log/cron.log
RUN mkdir /var/log/bot

# Not currently used, client program uses ephemeral ports
# EXPOSE 5545 5546  

# Main processes
CMD cron && python bot.py

# To start :
# `docker build -t "tagname" . `
# `docker run --name "containername" tagname`
