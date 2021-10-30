# Bloki

System bloków pozwala na łatwe tworzenie stałych fragmentów ramówki - zajawek, przypominajek, playlist.

### Klasy bloków
**Klasa bloków** to zestaw bloków które mają wspólne cechy:

- Ma swój zestaw plików audio
- Ma swój timetable
- Ma swoje sloty czasowe (np. 10 i 40. minuta każdej godziny)
- Może posiadać swój dźwięk otwierający i zamykający

Klasą bloków mogą być na przykład zajawki. 

## Tworzenie nowej klasy bloków

### Dodawanie katalogu
- W katalogu z bazą muzyczną (np *srv/radio/*) znajduje się katalog *block*. Tworzymy w nim katalog o nazwie takiej jak kod bloku. Na przykład dla zajawek możemy dać kod ZAJ.
- Tam możemy wrzucać pliki z zajawkami. Fajnie, gdyby nie miały zbyt długich nazw (np *halo1.wav*) i miały jeden format audio np. wav.
- Możemy tam wrzucić plik openingu o nazwie *(KOD)_open.wav* i/lub plik closingowy *(KOD)_close.wav* (np. *ZAJ_open.wav* i *ZAJ_close.wav*) - system automatycznie je wykryje.

### Dodawanie timetable'a
- Do podkatalogu *blocks* dodajemy plik *(KOD).csv* - najlepiej dodać go z szablonu.
- W pierwszej kolumnie dodajemy odpowiednie godziny
- W odpowiednie komórki wpisujemy odpowiednie wartości

#### Składnia
Do organizacji wykorzystano prostą składnię, upraszczającą zarządzanie systemem:
- `(pusta komórka)` - Nic nie odtworzy (nie odtworzy się opening i closing bloku)
- `plik.wav` - Odtworzy plik o tej nazwie.
- `plik` - Odtworzy plik o nazwie *plik.wav* jeśli jest w katalogu. Jeśli jest tam *plik.wav* i *plik.mp3* to odtworzy ten pierwszy Dopuszczalne rozszerzenia (w kolejności priorytetu) to wav, flac, mp3, ogg. 
- `plik1|plik2` - Odtworzy najpierw *plik1.wav* a potem *plik2.wav*
- `?` - Odtworzy losowo wybrany plik (musi mieć rozszerzenie audio)
- `??` - Odtworzy losowo 2 wybrane pliki, niepowtarzalne
- `????` - To samo tylko 4 razy :)
- `?|?|?` - Odtworzy 3 losowe pliki, mogą się powtórzyć
- `*` - Odtworzy wszystkie pliki w kolejności alfabetycznej po nazwie (np płyta tygodnia, jeśli ma odpowiednie indeksy).
