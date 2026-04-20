# Python-Übungen – Grundlagen für Schiffe Versenken

Hier lernst du die Python-Konzepte, die du für **Schiffe Versenken** brauchst. Jedes Thema enthält eine kurze Erklärung, Codebeispiele und Übungsaufgaben.

---

## Inhalte

1. [Texte aufteilen mit `split()`](#1-texte-aufteilen-mit-split)
2. [Mehrfachzuweisung mit `map()`](#2-mehrfachzuweisung-mit-map)
3. [Methoden definieren und aufrufen](#3-methoden-definieren-und-aufrufen)
4. [Listen als Arrays](#4-listen-als-arrays)
5. [Tupel](#5-tupel)
6. [Zeichen und ASCII: `chr()` und `ord()`](#6-zeichen-und-ascii-chr-und-ord)
7. [Mehrfachverzweigungen und geschachtelte Schleifen](#7-mehrfachverzweigungen-und-geschachtelte-schleifen)
8. [For-Schleifen mit iterierbaren Objekten](#8-for-schleifen-mit-iterierbaren-objekten)
9. [Generator-Ausdrücke und `all()`](#9-generator-ausdrücke-und-all)

---

## 1. Texte aufteilen mit `split()`

`split(trennzeichen)` zerlegt einen String anhand eines Trennzeichens und gibt eine **Liste** von Teilstrings zurück.

### Grundprinzip

```python
text = "Hallo,Welt,Python"
teile = text.split(",")   # ["Hallo", "Welt", "Python"]
print(teile[0])           # "Hallo"
print(teile[2])           # "Python"
```

### Im Spiel: Nachrichten auseinandernehmen

Wenn ein Spieler eine Nachricht wie `"SCHUSS:3,5"` empfängt, muss er Befehl und Koordinaten trennen:

```python
nachricht = "SCHUSS:3,5"

# Befehl und Parameter trennen
teile   = nachricht.split(":")   # ["SCHUSS", "3,5"]
befehl  = teile[0]               # "SCHUSS"
params  = teile[1]               # "3,5"

# Parameter weiter aufteilen
coords  = params.split(",")      # ["3", "5"]
zeile   = coords[0]              # "3"  (noch ein String!)
spalte  = coords[1]              # "5"
```

### Aufgaben

1. Gegeben: `s = "rot,grün,blau,gelb"`. Teile den String auf und gib das dritte Element aus.
2. Gegeben: `msg = "WASSER:7,2"`. Schreibe Code, der `befehl`, `zeile` und `spalte` als separate Variablen enthält.
3. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `parse_msg(msg)`, die eine Nachricht im Format `"BEFEHL:zeile,spalte"` entgegennimmt und ein [Tupel](#5-tupel) `(befehl, zeile, spalte)` zurückgibt (`zeile` und `spalte` als `int`).

---

## 2. Mehrfachzuweisung mit `map()`

`map(funktion, iterable)` wendet eine Funktion auf jedes Element einer Liste an. Das Ergebnis kann direkt auf mehrere Variablen *entpackt* werden.

### Schritt für Schritt

```python
# Ausgangspunkt: zwei Zahlen als Strings
koordinaten = ["3", "5"]

# int() auf jeden Eintrag anwenden
zahlen = map(int, koordinaten)   # entspricht [int("3"), int("5")]

# Ergebnis auf zwei Variablen verteilen (Unpacking)
zeile, spalte = zahlen
print(zeile)    # 3
print(spalte)   # 5
```

In einer einzigen Zeile – so steht es auch im Spiel:

```python
zeile, spalte = map(int, "3,5".split(","))
```

> **Hinweis:** `map()` liefert kein direktes Listen-Objekt. Du kannst es aber mit `list(...)` umwandeln: `list(map(int, werte))`

### Aufgaben

1. Gegeben: `text = "10,20,30"`. Nutze `map()`, um drei Integer-Variablen `a`, `b`, `c` zu befüllen.
2. Was passiert, wenn du `x, y = map(int, "3,5,7".split(","))` ausführst? Probiere es aus und erkläre die Fehlermeldung.
3. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `parse_coords(text)`, die einen String wie `"3,5"` entgegennimmt und ein [Tupel](#5-tupel) `(int, int)` zurückgibt.

---

## 3. Methoden definieren und aufrufen

Eine Funktion wird mit dem Schlüsselwort `def` definiert. Es gibt vier Grundvarianten:

| Variante | Beispiel |
|---|---|
| Kein Parameter, keine Rückgabe | `def gruss():` |
| Mit Parametern, keine Rückgabe | `def gruss(name):` |
| Kein Parameter, mit Rückgabe | `def zufallszahl():` |
| Mit Parametern und Rückgabe | `def addiere(a, b):` |

```python
# Kein Parameter, keine Rückgabe
def begruessung():
    print("Hallo!")

begruessung()   # Aufruf


# Mit Parametern, keine Rückgabe
def zeige_feld(zeile, spalte):
    print(f"Zeile {zeile}, Spalte {spalte}")

zeige_feld(3, 5)   # Aufruf


# Kein Parameter, mit Rückgabe
def spielname():
    return "Schiffe Versenken"

name = spielname()
print(name)


# Mit Parametern und Rückgabe
def addiere(a, b):
    return a + b

summe = addiere(3, 4)
print(summe)   # 7
```

### Aus dem Spiel: Aufruf mit Rückgabewert

```python
def check_sunk(ship_cells):
    # gibt True oder False zurück
    return all(my_grid[r][c] == HIT for (r, c) in ship_cells)

# Aufruf und Nutzung des Rückgabewerts:
if check_sunk(mein_schiff):
    print("Versenkt!")
```

### Aufgaben

1. Schreibe eine Funktion `begruessung(name)`, die `"Hallo, [name]!"` ausgibt. Rufe sie mit deinem Namen auf.
2. Schreibe eine Funktion `quadrat(n)`, die `n * n` zurückgibt. Gib das Ergebnis für `n = 7` aus.
3. Schreibe eine Funktion `ist_treffer(wert)`, die `True` zurückgibt, wenn `wert == "X"`, sonst `False`.
4. Schreibe eine Funktion `feld_name(zeile, spalte)`, die den Feldnamen zurückgibt (z.B. `zeile=3, spalte=5` → `"F4"`). Tipp: Spalte A = 0, B = 1, ... – nutze [`chr(65 + spalte)`](#6-zeichen-und-ascii-chr-und-ord).

---

## 4. Listen als Arrays

In Python werden Listen wie Arrays in anderen Sprachen verwendet. Sie können beliebige Werte speichern und wachsen dynamisch.

### Erstellen, Zugreifen, Verändern

```python
# Erstellen
farben = ["rot", "grün", "blau"]

# Zugreifen (Index beginnt bei 0)
print(farben[0])    # "rot"
print(farben[-1])   # "blau" (letztes Element)

# Verändern
farben[1] = "gelb"
print(farben)       # ["rot", "gelb", "blau"]

# Anhängen
farben.append("lila")

# Länge
print(len(farben))  # 4
```

### Zweidimensionale Listen (wie ein Spielfeld)

```python
# 3×3 Spielfeld als Liste von Listen
feld = [
    [".", ".", "."],
    [".", ".", "."],
    [".", ".", "."]
]

# Zugriff: feld[zeile][spalte]
feld[1][2] = "X"    # Zeile 1, Spalte 2 setzen
print(feld[1][2])   # "X"


# 10×10 Spielfeld erstellen
WATER = "."
my_grid = [[WATER] * 10 for _ in range(10)]
```

### Liste von Tupeln (wie Schiffskoordinaten)

```python
# Ein Schiff belegt Felder (0,0), (0,1), (0,2)
schiff = [(0, 0), (0, 1), (0, 2)]

# Über alle Felder des Schiffes iterieren
for (zeile, spalte) in schiff:
    print(f"Feld: Zeile {zeile}, Spalte {spalte}")
```

### Aufgaben

1. Erstelle eine Liste mit den Zahlen 1 bis 5 und gib das dritte Element aus.
2. Erstelle ein 4×4 Spielfeld (als Liste von Listen), bei dem alle Felder den Wert `"."` haben. Setze das Feld in Zeile 2, Spalte 3 auf `"X"`.
3. Gegeben: `my_ships = [[(0,0),(0,1)], [(3,5)], [(7,2),(7,3),(7,4)]]`. Gib aus, wie viele Schiffe es gibt und wie viele Felder das dritte Schiff belegt.
4. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `setze_schiff(grid, schiff_felder)`, die alle Felder aus `schiff_felder` im Grid auf `"S"` setzt.

---

## 5. Tupel

Ein **Tupel** ist wie eine Liste, aber *unveränderlich* (immutable). Tupel werden mit runden Klammern erstellt und eignen sich gut für zusammengehörige Werte wie Koordinaten.

### Erstellen und Zugreifen

```python
# Tupel erstellen
koordinate = (3, 5)       # Zeile 3, Spalte 5

# Zugreifen (wie bei Listen)
zeile  = koordinate[0]    # 3
spalte = koordinate[1]    # 5

# Entpacken (Unpacking) – sehr praktisch!
zeile, spalte = koordinate
print(zeile)    # 3
print(spalte)   # 5
```

### Tupel vs. Liste

| Eigenschaft | Liste `[]` | Tupel `()` |
|---|---|---|
| Veränderbar? | Ja | Nein |
| Für was? | Sammlungen, die sich ändern | Feste Wertepaare (z.B. Koordinaten) |

### Tupel in for-Schleifen entpacken

```python
schiff = [(0, 0), (0, 1), (0, 2)]

for (r, c) in schiff:
    print(f"Prüfe Feld ({r}, {c})")

# Kurzform ohne Klammern funktioniert auch:
for r, c in schiff:
    print(r, c)
```

### Aufgaben

1. Erstelle ein Tupel `schuss = (4, 7)` und entpacke es in `zeile` und `spalte`. Gib beide aus.
2. Erkläre: Was passiert, wenn du versuchst `schuss[0] = 9` auszuführen? Warum ist das so?
3. Gegeben: `treffer_liste = [(1,2), (1,3), (1,4)]`. Schreibe eine [for-Schleife](#8-for-schleifen-mit-iterierbaren-objekten), die jede Koordinate entpackt und `"Getroffen: Zeile X, Spalte Y"` ausgibt.
4. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `mittelpunkt(p1, p2)`, die zwei Koordinaten-[Tupel](#5-tupel) bekommt und den Mittelpunkt als neues Tupel zurückgibt. Beispiel: `mittelpunkt((2,4), (6,8))` → `(4, 6)`.

---

## 6. Zeichen und ASCII: `chr()` und `ord()`

Jedes Zeichen hat einen numerischen ASCII-Code. `chr(n)` wandelt eine Zahl in das entsprechende Zeichen um, `ord(c)` macht das Umgekehrte.

### Die wichtigsten Werte

| Funktion | Eingabe | Ergebnis | Erklärung |
|---|---|---|---|
| `chr(65)` | 65 | `"A"` | Großbuchstabe A |
| `chr(66)` | 66 | `"B"` | Großbuchstabe B |
| `chr(65+9)` | 74 | `"J"` | 10. Buchstabe (Spalte 9 → "J") |
| `ord("A")` | `"A"` | 65 | Rückrichtung |

### Im Spiel: Spaltennummer → Buchstabe

```python
# Spalte 0 → "A", Spalte 5 → "F", ...
def spalte_zu_buchstabe(spalte):
    return chr(65 + spalte)

print(spalte_zu_buchstabe(0))   # "A"
print(spalte_zu_buchstabe(5))   # "F"
print(spalte_zu_buchstabe(9))   # "J"


# Feldname aus Zeile und Spalte (z.B. 3,5 → "F4")
def feld_name(zeile, spalte):
    return chr(65 + spalte) + str(zeile + 1)

print(feld_name(3, 5))   # "F4"
print(feld_name(0, 0))   # "A1"
```

> **Warum `65 + spalte`?** Der ASCII-Code von `"A"` ist 65. Spalte 0 soll `"A"` sein, also ist Spalte *n* der Buchstabe mit Code 65 + n.

### Aufgaben

1. Welches Zeichen ergibt `chr(72)`? Finde die Antwort per Code.
2. Schreibe eine Schleife, die alle Spaltenbuchstaben A bis J ausgibt (also für Spalten 0 bis 9).
3. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `buchstabe_zu_spalte(buchstabe)`, die den umgekehrten Weg geht: `"A"` → 0, `"F"` → 5. Nutze `ord()`.
4. Erstelle eine [Liste](#4-listen-als-arrays) `spaltennamen`, die alle Buchstaben von A bis J enthält. Verwende eine List Comprehension mit `chr()`.

---

## 7. Mehrfachverzweigungen und geschachtelte Schleifen

### `if / elif / else` – Mehrfachverzweigung

Mit `elif` (kurz für "else if") prüft man mehrere Bedingungen nacheinander. Sobald eine passt, werden die anderen übersprungen.

```python
def bewerte_schuss(ergebnis):
    if ergebnis == "TREFFER":
        print("Volltreffer!")
    elif ergebnis == "WASSER":
        print("Daneben!")
    elif ergebnis == "VERSENKT":
        print("Schiff versenkt!")
    else:
        print("Unbekanntes Ergebnis")

bewerte_schuss("TREFFER")   # Volltreffer!
bewerte_schuss("WASSER")    # Daneben!
```

### Geschachtelte Schleifen

Für zweidimensionale Felder braucht man oft *Schleifen in Schleifen*. Die äußere läuft über die Zeilen, die innere über die Spalten.

```python
feld = [[".", "X", "."],
        [".", ".", "X"],
        ["X", ".", "."]]

for zeile in range(3):
    for spalte in range(3):
        if feld[zeile][spalte] == "X":
            print(f"Treffer bei ({zeile},{spalte})")
```

### `break` – Schleife vorzeitig beenden

`break` verlässt sofort die *innerste* Schleife, in der es steht. Das ist nützlich, wenn man etwas gefunden hat und nicht weitersuchen muss.

```python
gesuchtes_schiff = None

for schiff in my_ships:
    if (3, 5) in schiff:
        gesuchtes_schiff = schiff
        break            # gefunden – Schleife abbrechen

if gesuchtes_schiff:
    print("Schiff gefunden:", gesuchtes_schiff)
```

> **Wichtig:** `break` verlässt nur die direkt umgebende Schleife. Bei geschachtelten Schleifen läuft die äußere Schleife weiter.

### Aufgaben

1. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `noten_text(note)`, die bei 1→`"sehr gut"`, 2→`"gut"`, 3→`"befriedigend"`, 4→`"ausreichend"`, sonst→`"nicht bestanden"` zurückgibt. Nutze `if/elif/else`.
2. Erstelle ein 5×5 [Spielfeld (als Liste von Listen)](#4-listen-als-arrays) (alle Felder `"."`). Schreibe zwei geschachtelte Schleifen, die jedes Feld ausgeben – zeilenweise.
3. Gegeben: `zahlen = [3, 7, 1, 8, 2, 9, 4]`. Schreibe eine Schleife, die abbricht (`break`), sobald sie eine Zahl größer als 7 findet, und diese ausgibt.
4. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `finde_schiff(my_ships, zeile, spalte)`, die durch alle Schiffe iteriert und das Schiff zurückgibt, das das Feld `(zeile, spalte)` enthält. Nutze `break`. Gibt `None` zurück, wenn kein Schiff gefunden wird.

---

## 8. For-Schleifen mit iterierbaren Objekten

Ein **iterierbares Objekt** ist alles, über das man mit `for` Element für Element iterieren kann – z.B. Listen, Tupel, Strings oder `range()`.

### Über eine Liste iterieren

```python
farben = ["rot", "grün", "blau"]
for farbe in farben:
    print(farbe)
# Ausgabe: rot, grün, blau (je eine Zeile)
```

### Über eine Liste von Listen (Schiffe)

```python
my_ships = [
    [(0, 0), (0, 1), (0, 2), (0, 3)],   # Schlachtschiff
    [(3, 5), (4, 5), (5, 5)],            # Kreuzer
    [(7, 2)],                             # U-Boot
]

# Durch alle Schiffe iterieren
for schiff in my_ships:
    print(f"Schiff hat {len(schiff)} Feld(er): {schiff}")

# Durch alle Felder jedes Schiffes iterieren
for schiff in my_ships:
    for (r, c) in schiff:
        print(f"  Feld: ({r}, {c})")
```

### Was bedeutet "iterierbar"?

Python kann automatisch über jedes Objekt iterieren, das eine Sequenz von Elementen hat. Listen, Tupel, Strings und `range()` sind iterierbar.

```python
# String ist iterierbar: jeder Buchstabe ist ein Element
for buchstabe in "Hallo":
    print(buchstabe)

# range() liefert Zahlen
for i in range(5):
    print(i)    # 0, 1, 2, 3, 4
```

### Aufgaben

1. Gegeben: `my_ships = [[(0,0),(0,1)], [(3,5)], [(7,2),(7,3),(7,4)]]`. Gib für jedes Schiff aus: `"Schiff X hat Y Felder"`.
2. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `alle_felder(my_ships)`, die eine flache [Liste](#4-listen-als-arrays) aller belegten Felder zurückgibt. Beispiel: `[[(0,0),(0,1)], [(3,5)]]` → `[(0,0),(0,1),(3,5)]`.
3. Iteriere über den String `"SCHUSS:3,5"` und zähle, wie viele Zeichen Ziffern sind (nutze `.isdigit()`).
4. Schreibe eine Schleife, die alle Felder von `my_ships` durchgeht und prüft, ob das Feld `(3, 5)` enthalten ist. Gib `True` aus falls ja, sonst `False`.

---

## 9. Generator-Ausdrücke und `all()`

### `all()` – sind alle Elemente wahr?

`all(iterable)` gibt `True` zurück, wenn *alle* Elemente des Iterables wahr sind. Sobald ein Element `False` ist, gibt `all()` sofort `False` zurück.

```python
print(all([True, True, True]))    # True
print(all([True, False, True]))   # False
print(all([]))                    # True (leere Liste – Sonderfall!)
```

### Generator-Ausdruck

Ein **Generator-Ausdruck** sieht aus wie eine List Comprehension, steht aber in runden statt eckigen Klammern. Er berechnet Werte *eines nach dem anderen*, ohne alles auf einmal in den Speicher zu laden.

```python
# List Comprehension (erstellt eine vollständige Liste):
quadrate_liste = [x * x for x in range(5)]   # [0, 1, 4, 9, 16]

# Generator-Ausdruck (berechnet Werte bei Bedarf):
quadrate_gen = (x * x for x in range(5))
```

`all()` kann direkt einen Generator-Ausdruck verwenden – das ist effizient, weil es abbricht, sobald ein `False` auftritt.

### Im Spiel: Ist ein Schiff versenkt?

```python
HIT = "X"

my_grid = [
    ["X", "X", "X", "."],   # Zeile 0: alle drei Felder getroffen
    [".", ".", ".", "."],
]

ship_cells = [(0, 0), (0, 1), (0, 2)]

# Prüfung: sind alle Felder des Schiffes mit HIT markiert?
versenkt = all(my_grid[r][c] == HIT for (r, c) in ship_cells)
print(versenkt)   # True
```

Was passiert in dieser Zeile Schritt für Schritt?

```python
all(my_grid[r][c] == HIT for (r, c) in ship_cells)
```

1. Der Generator geht durch jedes Tupel `(r, c)` in `ship_cells`
2. Für jedes Tupel wird `(r, c)` entpackt
3. `my_grid[r][c] == HIT` ergibt `True` oder `False`
4. `all()` prüft: sind *alle* dieser Werte `True`?

> **Kurzschlussauswertung:** Sobald `all()` ein `False` trifft, hört es auf zu prüfen. Das spart Rechenzeit bei großen Listen.

### Verwandte Funktion: `any()`

```python
# any() gibt True zurück wenn MINDESTENS EIN Element True ist
zahlen = [1, 3, 7, 10, 2]
print(any(z > 8 for z in zahlen))   # True (10 > 8)
print(any(z > 20 for z in zahlen))  # False
```

### Aufgaben

1. Gegeben: `noten = [2, 1, 3, 2, 1]`. Nutze `all()`, um zu prüfen, ob alle Noten besser als 4 sind.
2. Erkläre in eigenen Worten, was die Zeile `all(my_grid[r][c] == HIT for (r,c) in ship_cells)` macht. Was wird für jedes `(r,c)` berechnet? Was gibt `all()` zurück?
3. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `check_sunk(ship_cells, grid)`, die `True` zurückgibt, wenn alle Felder des Schiffes im Grid den Wert `"X"` haben. Nutze `all()` mit einem Generator-Ausdruck.
4. Schreibe eine [Funktion](#3-methoden-definieren-und-aufrufen) `check_all_sunk(my_ships, grid)`, die `True` zurückgibt, wenn alle Schiffe in `my_ships` versenkt sind. Nutze `all()` und rufe darin `check_sunk()` auf.
5. Bonus: Was gibt `all([])` zurück? Teste es und erkläre, warum das Sinn ergibt.
