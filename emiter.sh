#rebuild all playlists
su liquidsoap -c "/home/liquidsoap/emiter/emiter.py rebuild_playlist all"

#create program dirs
/home/liquidsoap/emiter/emiter.py maintain

#run liquidsoap
su liquidsoap -c "/home/liquidsoap/.opam/4.08.0/bin/liquidsoap /home/liquidsoap/emiter/radio.liq -d"

#run cron
/usr/sbin/cron -f