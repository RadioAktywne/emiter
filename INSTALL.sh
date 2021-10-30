#!/bin/bash

mkdir log
#mkdir selektor
touch log/log.csv
touch log/playout.csv
#touch selektor/selektor_jin.csv
#touch selektor/selektor_mus.csv

echo "potrzebuję sudo by wgrać config do katalogu /etc"
sudo cp config.example /etc/emiter.conf
echo "Gotowe. Użyj 'sudo nano /etc/emiter.conf' by skonfigurować"

