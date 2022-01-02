import json

#default config using Docker config
cfg = {
    "telnet_port":"2137",

    "home_path": "/home/liquidsoap/emiter/",
    "path_schedules": "/home/liquidsoap/emiter/data/",
    "path_playlists": "/home/liquidsoap/emiter/data/",
    "path_auditions": "/srv/emiter/programs/",
    "path_temp_records": "/srv/emiter/record/",
    "path_spy": "/srv/emiter/spy/",
    "path_liquidsoap_bin": "/home/liquidsoap/.opam/4.08.0/bin/liquidsoap",
    "url_program_api":"https://localhost:8888/api",

    "input_studio_prefix":"",
    "input_studio_user":"source",
    "input_studio_password": "####",

    "output_prefix":"ra",
    "output_host": "localhost",
    "output_port": "8000",
    "output_password": "####",
    
    "output_name": "Radio Aktywne",
    "output_desc": "Radio Aktywne",
    "output_url": "http://radioaktywne.pl",

    "default_user": "liquidsoap",
    "file_uid": 115,
    "file_gid": 33,

    "spy_days_stored": 21,

    "auto_playlist_config":{
        "music_containers": {
            "MUSD": "/srv/emiter/playlist/music_day/",
            "MUSN": "/srv/emiter/playlist/music_night/",
            "JIN": "/srv/emiter/playlist/jingles/"
        },

        "playlists": {
            "muzyka_dzien": {

                "description":"Muzyka w dzień (6-22)",
                "mixing": {
                    "JIN":{
                        "min":1,
                        "max":1,
                        "track_repeat":3
                    },
                    "MUSD":{
                        "min":1,
                        "max":3,
                        "track_repeat":200,
                        "album_repeat":100,
                        "artist_repeat":50 
                    }
                }
            },
            "muzyka_noc": {

                "description":"Muzyka w nocy (22-6)",
                "mixing":{
                    "JIN":{
                        "min":1,
                        "max":1,
                        "track_repeat":3
                    },
                    "MUSN":{
                        "min":2,
                        "max":5,
                        "track_repeat":200,
                        "album_repeat":100,
                        "artist_repeat":50 
                    }
                }
            }
        }
    }
}

def update_recursive(dict1, dict2):
    ''' Update two config dictionaries recursively.

    Args:
        dict1 (dict): first dictionary to be updated
        dict2 (dict): second dictionary which entries should be used

    '''
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = dict()
        if isinstance(v, dict):
            update_recursive(dict1[k], v)
        else:
            dict1[k] = v


#read config from JSON file and overwrite default settings
with open('/etc/emiter.conf') as f:
    cfg_from_etc = json.load(f)
    update_recursive(cfg,cfg_from_etc)



