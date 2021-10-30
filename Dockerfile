FROM debian:10

ENV TZ Europe/Warsaw

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
    procps \
    ffmpeg

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
RUN mkdir /home/liquidsoap/tmp
WORKDIR /home/liquidsoap/tmp
COPY requirements.txt .
RUN pip3 install -r requirements.txt

#copy config file
#consider bind mount for changing conf from host in fly 
USER root
COPY emiter.conf /etc/

#create temporary record dir
RUN mkdir /srv/record/
RUN chown liquidsoap:liquidsoap /srv/record/

#create log dir
RUN mkdir /var/log/emiter/
RUN chown liquidsoap:liquidsoap /var/log/emiter

#create run dir
RUN mkdir /var/run/emiter/
RUN chown liquidsoap:liquidsoap /var/run/emiter

#set timezone
# ENV TZ does not work for cron
RUN ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime

#copy cron entries
COPY cron.tab /tmp/
RUN cat /tmp/cron.tab >> /etc/crontab
RUN rm /tmp/cron.tab


WORKDIR /home/liquidsoap/emiter

# START everything
# - rebuild playlists and start liquidsoap in bg (emiter.py start) TODO
# - run cron in fg
#ENTRYPOINT ["sh", "/home/liquidsoap/emiter"]

USER root
ENTRYPOINT ["/usr/sbin/cron", "-f"]
#ENTRYPOINT ["whoami"]