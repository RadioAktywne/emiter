# Emiter_core
Czyli ogólny package do ogarniania rzeczy "emiterowych". W ogólnym skrócie jest to zestaw narzędzi służący do tego, by takie operacje jak wrzucenie puszki, sprawdzenie ramówki czy wylistowanie wszystkich puszek na 24h do przodu móc zrobić w kilku linijkach, a nie dłubać po kolei wszysko

## Pokrótce co jest w konkretnych plikach

### cfg.py
import danych z /etc/emiter.conf, konwersja json -> słownik pythonowski cfg.cfg[]

### block.py 
Bloki np. zajawkowe - pobieranie w postaci a|b|c, dodawanie rozszerzenia, dokładanie bloku in/out. Tworzenie listy requestów do liquidsoapa

### schedule.py
Wszelkie operacje na csv-kach (np. ramówce, zajawkach). Odczyt slotów/audycji. Określanie, jaki slot / jaka audycja jest o danej porze, kiedy się zaczyna, kiedy kończy. 

### file.py
Operacje na plikach. Tworzenie nowych katalogów dla audycji, wykrywanie obecności plików z puszkami, archiwizacje, w przyszłości może jakieś czyszczenia. **Warto zajrzeć też do file_flow.md bo tam jest objaśnione jak to działa**. 

### liquidsoap.py
komunikacja skrypty -> liquidsoap. Parsowanie statusu. Wysyłanie komend socatem (wyparł request.sh)

### validate_file.py
Sprawdzenie, czy liquidsoap jest w stanie odtworzyc wskazany plik.

### server.py
Zarządzanie (urchamianie/zatrzymywanie) procesu emiter-server.py
