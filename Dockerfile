FROM python:3.9

WORKDIR /usr/bot
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# So that `RUN pip install ...` can be cached if rebuilding image

RUN apt-get update 
RUN apt-get -y install cron lsof less nano

RUN touch /etc/cron.d/cron-tasks
RUN chmod 0644 /etc/cron.d/cron-tasks
RUN touch /var/log/cron.log
RUN mkdir /var/log/bot

# Not currently used, client program uses ephemeral ports
# EXPOSE 5545 5546  

# Now copy all the files
ADD . .

RUN chmod 0755 entrypoint.sh
# Main processes
CMD ["bash", "./entrypoint.sh"]

# To start :
# `docker build -t "tagname" . `
# `docker run [-it] [--rm] [--name "containername"] tagname`
