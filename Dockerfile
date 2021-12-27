FROM debian:10

ENV TZ Europe/Warsaw

ENV AM_I_IN_DOCKER true

# Add package repo
RUN echo "deb http://deb.debian.org/debian stable main contrib non-free" > /etc/apt/sources.list

# Set up dependencies
RUN apt-get -y update && \
  apt-get -y install \
    dnsutils \
    telnet \
    build-essential \
    wget \
    curl \
    telnet \
    libmad0-dev \
    libshout3-dev \
    libvorbis-dev \
    libfdk-aac-dev \
    libid3tag0-dev \
    libmad0-dev \
    libshout3-dev \
    libasound2-dev \
    libpcre3-dev \
    libmp3lame-dev \
    libogg-dev \
    libtag1-dev \
    libssl-dev \
    libtool \
    libflac-dev \
    libogg-dev \
    libsamplerate-dev \
    libavutil-dev \
    libopus-dev \
    libgnutls28-dev \
    libsrt-gnutls-dev \
    autotools-dev \
    autoconf \
    automake \
    ocaml-nox \
    opam \
    m4 \
    cron \
    vim \
    python3 \
    python3-pip \
    socat \
    procps

# Set up filesystem and user
USER root

#tworzenie usera/grupy liquidsoap
#tu trzeba wrzucic uid i gid usera liquidsoap z systemu
RUN groupadd -g 123 liquidsoap
RUN useradd -u 115 -g 123 -s /bin/bash -m liquidsoap

RUN mkdir /var/log/liquidsoap
RUN chown -R liquidsoap:liquidsoap /var/log/liquidsoap
RUN chmod 766 /var/log/liquidsoap

# Switch over so we can install OPAM
USER liquidsoap

# Initialize OPAM and install Liquidsoap and asssociated packages
RUN echo n | opam init --disable-sandboxing
RUN opam switch create 4.08.0
RUN eval `opam config env`
RUN opam install -y ssl opus cry flac inotify lame mad ogg fdkaac samplerate taglib vorbis xmlplaylist srt liquidsoap

# Install python requirements
#RUN mkdir /home/liquidsoap
WORKDIR /home/liquidsoap
COPY requirements.txt .
USER root
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

#add files to /home/liquidsoap/emiter TODO in release
COPY --chown=liquidsoap:liquidsoap emiter/ /home/liquidsoap/emiter/
RUN chmod +x /home/liquidsoap/emiter/emiter.py

WORKDIR /home/liquidsoap/emiter

# START everything
# - rebuild playlists and start liquidsoap in bg (emiter.py start) TODO
# - run cron in fg
ENTRYPOINT ["sh", "/home/liquidsoap/emiter.sh"]

#ENTRYPOINT ["/usr/sbin/cron", "-f"]
