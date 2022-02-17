%include "orban.liq"


#pobieranie configu
cfg_path = argv(default="/etc/emiter.conf",1)
cfg_file = file.contents(cfg_path)
cfg = json.parse(default=[("","")], cfg_file)

home_path = cfg["home_path"]
playlist_path = cfg["path_playlists"]

settings.log.file.path.set("/var/log/emiter/liquidsoap.log") #ścieżka do loga
settings.log.stdout.set(true)

#telnet - w celach debugowych
settings.server.telnet.set(true)
settings.server.telnet.bind_addr.set("127.0.0.1")
settings.server.telnet.port.set(int_of_string(cfg["telnet_port"]))
settings.server.timeout.set(-1.)

#socket - do integracji
settings.server.socket.set(true)
settings.server.socket.path.set("/var/run/emiter/socket")

settings.init.daemon.pidfile.path.set(home_path^"radio.pid")
settings.init.daemon.pidfile.set(true)

def generate_playlist(pl_code)

	pfile = playlist_path^pl_code^".csv"
	plist = ref([])
		
	def reload_playlist_file() =
		plist := string.split(separator="\n",file.contents(pfile))
		log("playlist "^pl_code^" reloaded")
	end
	ignore(file.watch(pfile,reload_playlist_file))
	reload_playlist_file()

	#Funkcja requestująca
	def new_request() =
		
		#flip playlist stack
		row = list.hd(default="",!plist)
		plist := list.tl(!plist)
		plist := list.append(!plist, [row])

		sep_row = string.split(separator=";",row)
		code = list.nth(default="",sep_row,0)
		file = list.nth(default="",sep_row,1)

		#stwórz request i przechowaj czas w metadanych
		#TODO wylicz długość utworu i podaj do annotate
		rq = request.create('annotate:code="'^code^'":'^file)

		#zwróć request
		[rq]
	end

	id = "playlista_"^pl_code
	request.dynamic(id=id,prefetch=4,new_request, timeout=6.)
end

now_meta = ref([])

def capture_meta(m)
	#przechwyt metadanych

	if m["filename"] != "" or m["source"] == "studio" then
		now_meta := m
	end

	file_path = "/var/log/emiter/log.csv"
	
	timestamp = int_of_float(time())
	code = m["code"]
	artist = m["artist"]
	title = m["title"]
	album = m["album"]
	audio_file = m["filename"]

	log_record = "#{timestamp}\t#{code}\t#{title}\t#{artist}\t#{album}\t#{audio_file}\n"

	file.write(data=log_record, append=true, file_path)

	#nic nie zwracaj
	ignore(false)
end

#jingiel startowy
#potrzebny po to, ze po odpaleniu skryptu playlista potrzebuje trochę czasu by się wygenerować 
init_jingle = once(single(id="startowy",home_path^"audio/start.wav"))

#playlista generowana za pomocą funkcji request.dynamic ze stackowaniem utworów na playliście
playlist_d= generate_playlist("muzyka_dzien")
playlist_n= generate_playlist("muzyka_noc")

playlist = switch([( {06h00m - 22h00m}, playlist_d ), ({ true }, playlist_n )])
playlist = normalize(target=-17., window = 0.03, gain_min= -32., gain_max = 0., playlist)

#żródła requestowe na puszki/bloki
playout = request.queue(id="playout")
block   = request.queue(id="block")

#bbuduj program (puszki, bloki, playlista)
PGM_standby = fallback([playout,block,playlist])

def mqtt_publish_playlist(current_track_meta)
	# aktualizuj metadane w now_meta
	now_meta := current_track_meta

	#TODO
	# publikuj info o nowej ścieżce i kolejce

	# if current_track_meta["source"] == "playlista_muzyka_dzien" then
	# 	list.iter(build_json_meta,playlist_d.queue())
	# end

end
PGM_standby.on_track(mqtt_publish_playlist)

#dodatkowy bind po rozłączeniu się ze studiem
def studio_flag_down()
	log("Zakonczono transmisję live")
end

#gdy studio startuje - podnieś flagę
studio_up = ref(false)
def studio_flag_up(_)
	log("Rozpoczęto transmisję live")
	#log("Flaga podnies")
	studio_up := true
end

#input (dosył) ze studia
PGM_studio=input.harbor("studio", 
		id="studio_nometa",
		buffer=0.5,
		user=cfg["input_studio_user"], 
		password=cfg["input_studio_password"], 
		port=8009,
		on_disconnect=studio_flag_down,
		on_connect=studio_flag_up
)

def add_source_studio(m)
	ignore(m)
	[("source", "studio")]
end
PGM_studio = map_metadata(id="studio",add_source_studio,PGM_studio)

def crosstrack(~czas_przejscia=2., ~margin=4., ~medium=-4., ~high=-15., ~width=2.,s)

 	czas = ref(czas_przejscia)
	add = fun (a,b) -> add(normalize=false,[b, a])

	def transition(ending,starting)
		#obsługa przejść między utworami 

		#gdy flaga studia podniesiona
		#pomija całkowicie poprzedni utwór (ten który grał przed startem studia)
		#
		if !studio_up then
			#zeruj flagę
			studio_up := false
			#pomiń całkowicie poprzedni utwór
			sequence([starting.source])
		else
			if starting.metadata["source"] == "playout" and ending.metadata["source"] != "playout" then
				#gdy zaczyna się puszka
				log("przejscie przed pucha")
				add(fade.out(duration=1.,ending.source),starting.source)
			#pozostałe tranzycje
			elsif starting.db_level>= ending.db_level+ margin and ending.db_level<= medium and starting.db_level<= high then
				#oba utwory konczą się cicho, 
				add(ending.source,starting.source)
			elsif ending.db_level<= medium and starting.db_level<= medium and abs( ending.db_level- starting.db_level) <= margin then
				#oba utwory kończą się głośno
				sequence([ending.source,starting.source])
			else
				#jeden cicho, drugi głośno
				add(ending.source,starting.source)
			end
		end
	end

	cross(width=width, duration=!czas, conservative=true, transition, s)
end

PGM_standby = crosstrack(PGM_standby)


#przejście gdy rozpoczyna się live
def live_start(standby,live) =
		#fade-out ostatniego utworu do zera, wejście live_a
	add = fun (a,b) -> add(normalize=false,[b, a])
	add(fade.out(duration=1.,track_sensitive=false,standby),live)
end

#przejście gdy kończy się live
def live_stop(live,standby) = 
	add = fun (a,b) -> add(normalize=false,[b, a])
	#pomiń ostatni utwór z playlisty
	source.skip(standby)
	#szybki fade in playlisty (filtruje stuki po skipie)
	add(live,fade.in(duration=0.3,track_sensitive=false,standby))
end

#aplikuj przejścia między studiem a automatem
radio = fallback(track_sensitive=false, transition_length=1.2, transitions=[live_start, live_stop], [PGM_studio,PGM_standby])

#mapowanie metadanych do funkcji zapisującej do loga
radio.on_metadata(capture_meta)

#dodaj backup i jingiel statowy
safe = single(home_path^"audio/radioniedziala.mp3")
radio = fallback(transition_length=2.,[radio,init_jingle,safe])

#postprocessing - do srogiego dostrojenia, normalizacja szaleje z poziomami.
radio = orban(radio)

#wyjściowe streamy
output.icecast(%vorbis(quality=0.8), 
	id = "PGM", 
	icy_metadata="false",
	encoding="UTF-8",
	host = cfg["output_host"], 
	port = int_of_string(cfg["output_port"]), 
	password = cfg["output_password"], 
	mount = cfg["output_prefix"]^"ogg",
	genre = "",
	name = cfg["output_name"],
	description = cfg["output_desc"],
	url = cfg["output_url"],
	radio)

# output.icecast(%mp3(bitrate=256), 
# 	id = "PGM_mp3", 
# 	icy_metadata="false",
# 	encoding="UTF-8",
# 	host = cfg["output_host"], 
# 	port = int_of_string(cfg["output_port"]), 
# 	password = cfg["output_password"], 
# 	mount = cfg["output_prefix"]^"mp3",
# 	genre = "",
# 	name = cfg["output_name"],
# 	description = cfg["output_desc"],
# 	url = cfg["output_url"],
# 	radio)

#szpieg
output.file(%vorbis(quality=0.6),cfg["path_spy"]^"%Y-%m-%d_%H-%M-%S.ogg",radio,reopen_when={0m},fallible=true)

#nagrywanie live'a
#dzieli bloki wg metadanych 
def on_file(fname)
	log("Reanaming closed file: mv '#{fname}' '#{fname}.ogg'")
	process.run("mv '#{fname}' '#{fname}.ogg'")

end
output.file(%vorbis(quality=0.8), cfg["path_temp_records"]^"%Y-%m-%d_%H-%M-%S_$(album)", PGM_studio,
reopen_on_metadata=true, reopen_when={03m}, on_close=on_file, fallible=true)

#czy do playout/block jest dodany port?
def playout_ready(_)
	source.is_ready(playout) or source.is_ready(block)
end


#status - Zwraca dane w JSON o aktualnie granym tracku i stanie ogólnym systemu
#TODO
def send_status(_)
	meta = !now_meta
	playout_rdy = playout_ready("")
	stat = json()

	if PGM_studio.is_ready() then
		stat.add("source","studio")
		stat.add("code","LIVE")
		stat.add("on_air_timestamp",-1)
		stat.add("filename","")

		if meta["source"] == "studio" then
		
			#studio aktywne i zaktualizowano metadane
			stat.add("title",meta["title"])
			stat.add("artist",meta["artist"])
			stat.add("program_code",meta["album"])
			
		else
			#studio aktywne ale jeszcze nie zaktualizowano metadanych
			#dodaj standardowe (puste) dane
			stat.add("title","")
			stat.add("artist","")
			stat.add("program_code","unknown")
		end
	else
		#studio nieaktywne, gra automat (standby)
		stat.add("source",meta["source"])
		stat.add("code",meta["code"])
		stat.add("on_air_timestamp",int_of_float(float_of_string(meta["on_air_timestamp"])))
		stat.add("title",meta["title"])
		stat.add("artist",meta["artist"])
		stat.add("program_code","")
		stat.add("filename",meta["filename"])
	end
	
	#playout_rdy=playout_ready("")
	stat.add("playout_ready",playout_rdy)

	#zwróć dane w JSON
	json.stringify(stat)

end
server.register("status",send_status)

#Close app using telnet/socket cmd
def shutdown_app(_)
	shutdown()
	"Done"
end
server.register("shutdown",shutdown_app)