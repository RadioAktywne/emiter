#!/bin/bash

#create temporary record dir
mkdir /srv/record/
chown liquidsoap:liquidsoap /srv/record/

#create log dir
mkdir /var/log/emiter/
chown liquidsoap:liquidsoap /var/log/emiter

#create run dir
mkdir /var/run/emiter/
chown liquidsoap:liquidsoap /var/run/emiter

#create data dir
mkdir /home/liquidsoap/emiter_data
chown liquidsoap:liquidsoap /home/liquidsoap/emiter_data
