#!/bin/bash

#create audio dirs
mkdir /srv/emiter
mkdir /srv/emiter/record
mkdir /srv/emiter/programs
mkdir /srv/emiter/playlist
chown -R liquidsoap:liquidsoap /srv/emiter

#create log dir
mkdir /var/log/emiter/
chown liquidsoap:liquidsoap /var/log/emiter

#create run dir
mkdir /var/run/emiter/
chown liquidsoap:liquidsoap /var/run/emiter

#create data dir
mkdir /home/liquidsoap/emiter_data
chown liquidsoap:liquidsoap /home/liquidsoap/emiter_data
