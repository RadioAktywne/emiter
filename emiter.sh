#rebuild all playlists
su liquidsoap -c "/home/liquidsoap/emiter/emiter.py rebuild_playlist all"

#create program dirs
/home/liquidsoap/emiter/emiter.py maintain

#run liquidsoap
su liquidsoap -c "/home/liquidsoap/emiter/emiter.py start"

#run cron
/usr/sbin/cron -f