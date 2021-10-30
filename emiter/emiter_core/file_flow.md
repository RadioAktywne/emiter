## File flow w emiterze

### 1. Przed audycją/puszką

Wykonuje się skrypt emiter.py archive_replay:
- Przerzuca plik z katalogu /powtorka (gdzie rezyduje nagranie z ostatniej audycji) do /archiwum
- Jeśli w katalogu /puszka jest puszka, kopuje go do /powtorka

### 2. Audycja na żywo
Audycja na żywo nagrywa się do katalogu /powtorka
  
### 3. Po audycji: 
Po audycji skrypt emiter.py remove_playout usuwa puszkę z katalogu /puszka

### Po co taki system?
Ma zlikwidować podstawowe problemy starego systemu:
- każda audycja musi mieć powtórkę (za wyjątkiem Grabka i gnp)
- powtórka może być tylko jedna na jedną audycję

Generalnie system działa tak, że **w katalogu /powtórka zawsze jest nagranie ostatniej nagranej audycji**. Wyjątkiem jest sytuacja, gdy audycja się nie odbędzie, wtedy katalog jest pusty. Oznacza to, że system może wielokrotnie w tygodniu requestować odtworzenie tej powtórki. Może też nie requestować jej nigdy.
