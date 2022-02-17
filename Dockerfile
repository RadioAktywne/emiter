FROM savonet/liquidsoap:v2.0.2
USER root

ENV TZ Europe/Warsaw

ENV AM_I_IN_DOCKER true

# Set up dependencies
RUN apt-get -y update && \
  apt-get -y install \
    dnsutils \
    telnet \
    libmad0-dev \
    build-essential \
    wget \
    curl \
    m4 \
    cron \
    vim \
    python3 \
    python3-pip \
    socat \
    procps

# Set up filesystem and user
USER root

#zmiana usera/grupy liquidsoap
#tu trzeba wrzucic uid i gid usera liquidsoap z systemu
RUN groupmod -g 123 liquidsoap
RUN usermod -u 115 -s /bin/bash liquidsoap

RUN mkdir /home/liquidsoap
RUN chown liquidsoap:liquidsoap /home/liquidsoap

WORKDIR /tmp
COPY requirements.txt .
RUN pip3 install -r requirements.txt

#copy config file
#consider bind mount for changing conf from host in fly 
COPY emiter.conf /etc/

#set timezone
# ENV TZ does not work for cron
RUN ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime

#copy cron entries
COPY cron.tab /tmp/
RUN cat /tmp/cron.tab >> /etc/crontab
RUN rm /tmp/cron.tab

#pre-instalation commands (create dirs in /var/log, /var/run etc.)
COPY INSTALL.sh /tmp/
RUN sh /tmp/INSTALL.sh
RUN rm /tmp/INSTALL.sh

#all commands to run at entrypoint
COPY emiter.sh /home/liquidsoap/

#add files to /home/liquidsoap/emiter
COPY --chown=liquidsoap:liquidsoap emiter/ /home/liquidsoap/emiter/
RUN chmod +x /home/liquidsoap/emiter/emiter.py

WORKDIR /home/liquidsoap/emiter

# START everything
# - rebuild playlists and start cron in bg
# - run liquidsoap in fg
ENTRYPOINT ["sh", "/home/liquidsoap/emiter.sh"]
