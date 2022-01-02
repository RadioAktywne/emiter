# Emiter
Emiter to system zarządzania emisją radia internetowego dla systemów Linux.

## Najważnejsze cechy
- Architektura klient-serwer. Poza audycjami na żywo, emiter zapewnia nieprzerwaną, zautomatyzowaną emisję bez konieczności ingerencji człowieka z poziomu serwera.
- Automatyczne budowanie playlist z możliwością ustalania arbitrażu.
- Programowalna ramówka w systemie tygodniowym za pomocą pliku z użyciem zewnętrznego API lub pliku .json.
- Automatyczne odtwarzanie audycji z serwera plików
- Automatyczne powtórkowanie audycji na żywo
- Logowanie odtworzonych ścieżek (historia odtworzonych utworów)
- Streamowanie programu do serwera icecast2

To repozytorium zawiera oprogramowanie serwerowe. Dedykowana aplikacja kliencka znajduje się tu: github.com/RadioAktywne/emiter-client.

## Instalacja
Instalacja została opisana tutaj: https://github.com/RadioAktywne/emiter/wiki/Instalacja

## Overview
Emiter bazuje na liquidsoapie w wersji 2.0 (https://www.liquidsoap.info/doc-2.0.0/reference.html) jako generatorowi streamu oraz na skryptach w Pythonie do automatyzacji emisji. Do wywoływania skryptów w reżimie czasowym należy użyć Crona.

## Konfiguracja
Config jest teraz zasysany z zewnętrznego pliku */etc/emiter.conf*. Dokładny opis konfiguracji znajduje się tutaj: https://github.com/RadioAktywne/emiter/wiki/Plik-konfiguracyjny.
