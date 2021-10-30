# emiter
System zarządzania emisją dla systemów Linux

## Najważnejsze cechy
- Architektura klient-serwer. Poza audycjami na żywo, emiter zapewnia nieprzerwaną, zautomatyzowaną emisję bez konieczności ingerencji człowieka z poziomu serwera.
- Automatyczne budowanie playlist z możliwością ustalania arbitrażu.
- Programowalna ramówka w systemie tygodniowym za pomocą pliku .csv lub z użyciem zewnętrznego API (w trakcie prac).
- Automatyczne odtwarzanie audycji z serwera plików
- Automatyczne powtórkowanie audycji na żywo
- Logowanie odtworzonych ścieżek
- Streamowanie programu do serwera icecast2 i/lub wyjście na kartę dźwiękową

Oprócz emiter-server (to repozytorium) powstaje rozwiązanie klienckie (zdalny podgląd systemu i obsługa audycji na żywo): github.com/hbiedka/emiter-client.

## Instalacja
Rekomenduje się instalację na systemie Debian w wersji 9+ lub bazującym na Debianie np. ubuntu.

Dokładna instrukcja instalacji: https://docs.google.com/document/d/1o6RAYk-STKbbgjQZ3nezhAytQJ5nd6iz_En-EnkE6u8/edit?usp=sharing

W trakcie prac również możliwość pracy w kontenerze Dockera.


## Overview
Emiter bazuje na liquidsoapie w wersji 1.4.2 (https://www.liquidsoap.info/doc-1.4.2/reference.html) jako generatorowi streamu oraz na skryptach w Pythonie do automatyzacji emisji. Do wywoływania skryptów w reżimie czasowym należy użyć Crona.

## Konfiguracja
Config jest teraz zasysany z zewnętrznego pliku */etc/emiter.conf*. Tam są ścieżki do plików i hasła. Przy instalacji skrypt install.sh kopiuje szablon configu config.example do /etc. Po inicjacji należy zedytować ten plik by skonfigurować system.

## Co robią poszczególne pliki?
### radio.liq (liquidsoap)

Skrypt główny liquidsoapa, który odpowiada za generowanie streamu radiowego.
Po odpaleniu skryptu radio startuje. Zatrzymanie tego pliku to zatrzymanie emisji.

**Zadania skryptu**
- Buforowanie playlisty poprzez dodawanie kolejnych plików z kontenerów muzyki (muzyka, jingle itd.) na podstawie wcześniej przygotowanych playlist. Aktualnie są dwie playlisty - *muzyka_dzien* i *muzyka_noc* zmieniane w godzinach 22:00 i 6:00
- Udostępnianie zewnętrznego inputu live ze studia
- Udostępnianie kolejki zewnętrznych requestów *playout* do odtwarzania puszek/powtórek wysyłanych przez skrypty automatyki
- miksowanie źródeł
- cross-tracking
- logowanie zagranej muzyki do pliku *log/log.csv*
- Dodatkowy stream in/out do streamów spoza studia
- Wysyłka do serwera icecast2
- Wysyłka na fizyczne wyjście audio (ALSA) z małym lagiem
- System do automatycznego nagrywania audycji
- dodatkowo skrypt tworzy socket pozwalający na komunikacje przez Telnet (wykorzystywaną przez klienta) ze skryptami. Wywołanie w telnecie funcji get <funkcja> wywołuje skrypt emiter.py get <funkcja>, a do klienta zwracana jest odpowiedź z stdoutu.

### orban.liq (liquidsoap)
Opcjonalny post-processing za pomocą otwartoźródłowych wtyczek audio (normalizacja, kompresja itd.)

### katalog emiter_core
Tu znajduje
Package pythonowy z modułami importowana przez skrypty. Więcej info w readme w katalogu.

### emiter.py 
Skrypt główny systemu, przyjmujący wszystkie polecenia od użytkownika oraz z Crona w celu zautomatyzowanego wykonywania zadań (odtwarzania playoutów, przenoszenia plików, aktualizacji playlist itd.)
Poszczególne funkcje realizujemy w katalogu *emiter_core*, ten skrypt ma je scalać.

#### przykładowe komendy

``- emiter.py start/stop/restart`` - uruchamia/zatrzymuje/resetuje system emisyjny (oraz z automatu rebuilduje wszystkie playlisty)

``- emiter.py push playout`` - sprawdza, czy nie zaczyna się puszka/powtórka i dodaje request

``- emiter.py archive_replay`` - sprawdza, czy zbliża się audycja, przerzuca powtórkę do archiwum, kopiuje puszkę do powtórki

``- emiter.py remove_playout`` - sprawdza, czy skończyła się jakaś audycja, jeśli tak to usuwa jej puszkę

``- emiter.py get playouts`` - zwraca w JSONie listę planowanych dziś puszek/powtórek/bloków (używa jej klient)

``- emiter.py get auds`` - zwraca w JSONie listę audycji (używa jej klient)

``- emiter.py rebuild_playlist <nazwa>`` - generuje na nowo playlistę

``- emiter.py rebuild_playlist all`` - generuje na nowo wszystkie playlisty

**przykładowy crontab dla rastru półgodzinnego** (zakładamy, że właścicielem skryptów jest user *liquidsoap*):
```
#na minutę przed (pół)godziną sprawdź ramówkę i wrzuć plik audio, jeśli zaczyna się jakaś audycja
29,59 * * * *   liquidsoap  /home/liquidsoap/emiter/emiter.py push playout

# jeśli do miunty po planowanym rozpoczęciu audycji nie skończył się ostatni utwór, wymuś jego zatrzumanie
1,31 * * * *    liquidsoap  /home/liquidsoap/emiter/emiter.py force_skip

#na 10 minut przed audycją archiwizuj ostatnią powtórkę
20,50 * * * *   liquidsoap  /home/liquidsoap/emiter/emiter.py archive_replay

#2 minuty po końcu audycji usuń plik z puszką
2,32 * * * *    liquidsoap  /home/liquidsoap/emiter/emiter.py remove_playout
```

### wavdur.py
Dodatkowy skrypt zwracający czas trwania pliku .wav podanego w argumencie. Używany przez liquidsoapa bo ten defaultowo liczy je źle.

### katalog audio/
Zawiera plik startowy odtwarzany przy starcie systemu oraz plik backupowy *radioniedziala.ogg* używany w razie awarii

### config.example
Szablon configu.

### INSTALL.sh
Skrypt instalacyjny - tworzy podstawowe pliki w systemie i kopiuje plik config.example do /etc
