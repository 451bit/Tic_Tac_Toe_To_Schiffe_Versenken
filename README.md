# 🚢 Von Tic-Tac-Toe zu Schiffe Versenken

Ein Schulprojekt für Klasse 11 zur Netzwerkprogrammierung mit Python.

## Projektbeschreibung

Dieses Repository enthält eine schrittweise Einführung in die Netzwerkprogrammierung. Ausgehend von einem fertigen Tic-Tac-Toe-Netzwerkspiel sollen Schüler ein vollständiges **Schiffe Versenken**-Spiel entwickeln, das über das lokale Netzwerk gespielt wird.

Der Schwerpunkt liegt auf dem **Entwurf eines eigenen Netzwerkprotokolls** und der **Implementierung der Spiellogik** – nicht auf der GUI, die bereits vollständig vorgegeben ist.

---

## Dateien im Überblick

| Datei | Beschreibung |
|---|---|
| `tictactoe_gui_net.py` | Fertiges Tic-Tac-Toe als Netzwerkspiel (Referenz & Einstieg) |
| `schiffe_versenken_vorlage.py` | Vorlage für das Schiffe Versenken (GUI fertig, Protokoll fehlt) |
| `ANLEITUNG.md` | Ausführliche Schritt-für-Schritt-Anleitung für Schüler |
| `PROTOKOLL_ANLEITUNG.md` | Leitfaden zum Entwurf des Netzwerkprotokolls |

---

## Voraussetzungen

- Python 3.8 oder höher
- Keine zusätzlichen Bibliotheken nötig (nur Python-Standardbibliothek)
- Zwei Computer im gleichen Netzwerk (oder ein Computer für lokale Tests)

---

## Schnellstart

### Schritt 1: Tic-Tac-Toe ausprobieren (Einstieg)

Öffnet zwei Terminal-Fenster:

```bash
# Terminal 1 – Server
python tictactoe_gui_net.py
# → "Server" eingeben

# Terminal 2 – Client (auf demselben Computer: IP = 127.0.0.1)
python tictactoe_gui_net.py
# → "Client" eingeben
# → IP-Adresse eingeben: 127.0.0.1
```

### Schritt 2: Vorlage starten

```bash
# Terminal 1 – Server
python schiffe_versenken_vorlage.py
# → "Server" eingeben

# Terminal 2 – Client
python schiffe_versenken_vorlage.py
# → "Client" eingeben
# → IP-Adresse eingeben: 127.0.0.1
```

Schiffe platzieren funktioniert bereits – das Protokoll müsst ihr selbst implementieren!

---

## Spielregeln

**Spielfeld:** 10×10 Felder (Spalten A–J, Zeilen 1–10)

**Flotte** (jeder Spieler):
- 1 × Schlachtschiff (Länge 4)
- 2 × Kreuzer (Länge 3)
- 3 × Zerstörer (Länge 2)
- 4 × U-Boot (Länge 1)

**Spielverlauf:**
1. Beide Spieler verbinden sich
2. Beide setzen ihre Schiffe (sichtbar nur für sich selbst)
3. Beide klicken "Fertig"
4. Das Spiel beginnt – Spieler schießen abwechselnd
5. Wer zuerst alle Schiffe des Gegners versenkt, gewinnt

---

## Lernziele

Nach diesem Projekt könnt ihr:

- **Client-Server-Architekturen** erklären und umsetzen
- **Sockets** in Python für Netzwerkverbindungen nutzen
- Ein einfaches **Textprotokoll** entwerfen und dokumentieren
- **Threads** für parallele Aufgaben (GUI + Netzwerk) einsetzen
- **Spiellogik** (Treffer, Versenkt, Spielende) implementieren

---

## Projektablauf für den Unterricht

```
Phase 1: Einstieg          (~20 min)
  └─ Tic-Tac-Toe spielen und Code lesen
  └─ Vorlage starten und GUI erkunden

Phase 2: Protokollentwurf  (~30 min)
  └─ PROTOKOLL_ANLEITUNG.md lesen
  └─ Gemeinsam Protokoll entwerfen und dokumentieren
  └─ Ergebnis: UNSER_PROTOKOLL.md

Phase 3: Implementierung   (~90 min)
  └─ ANLEITUNG.md Schritt für Schritt folgen
  └─ Aufgaben 1–8 in schiffe_versenken_vorlage.py lösen
  └─ Testen auf einem Computer (127.0.0.1)

Phase 4: Netzwerktest      (~20 min)
  └─ Spiel zwischen zwei Computern testen
  └─ Debugging falls nötig

Phase 5: Präsentation      (~30 min)
  └─ Protokollentscheidungen erklären
  └─ Besondere Lösungsansätze vorstellen
```

---

## Technische Hintergründe

### Verwendete Konzepte

**Sockets (Netzwerkkommunikation):**
```python
# Server                          # Client
sock = socket.socket(...)         sock = socket.socket(...)
sock.bind(("", 65432))            sock.connect(("192.168.1.42", 65432))
sock.listen(1)
conn, addr = sock.accept()        conn = sock
# Beide können jetzt senden und empfangen
conn.sendall("Hallo\n".encode())  data = conn.makefile().readline()
```

**Threading (gleichzeitig GUI + Netzwerk):**
```python
def receive_loop():
    for line in conn.makefile("r"):
        handle_message(line.strip())

threading.Thread(target=receive_loop, daemon=True).start()
```

**Protokoll (Textbasiert mit `:`-Trennzeichen):**
```
FERTIG          → kein Parameter
SCHUSS:3,5      → Zeile 3, Spalte 5
TREFFER:3,5     → Treffer auf (3,5)
WASSER:3,5      → Verfehlt auf (3,5)
VERSENKT        → Schiff vollständig versenkt
VERLOREN        → Alle Schiffe versenkt, ich habe verloren
```

---

## Lizenz

Dieses Projekt wurde für Bildungszwecke erstellt. Freie Nutzung und Anpassung für den Schulunterricht ausdrücklich erwünscht.
