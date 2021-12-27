#rebuild all playlists
su liquidsoap -c "/home/liquidsoap/emiter/emiter.py rebuild_playlist all"

#create program dirs
/home/liquidsoap/emiter/emiter.py maintain

#run API server
su liquidsoap -c "uvicorn api:app --port 10000 --host 0.0.0.0 --log-level warning --reload &"

#run cron
/usr/sbin/cron

#run liquidsoap
su liquidsoap -c "/home/liquidsoap/.opam/4.08.0/bin/liquidsoap /home/liquidsoap/emiter/radio.liq"