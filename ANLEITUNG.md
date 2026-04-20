# Schiffe Versenken – Projektanleitung für Klasse 11

## Überblick

In diesem Projekt erweitert ihr eine Netzwerk-Vorlage zu einem vollständigen **Schiffe Versenken**-Spiel, das über das lokale Netzwerk gespielt werden kann.

**Was ihr lernt:**
- Wie Netzwerkkommunikation zwischen zwei Computern funktioniert
- Wie man ein eigenes Netzwerkprotokoll entwirft
- Wie man Spiellogik umsetzt
- Wie Threads parallele Aufgaben ermöglichen

**Was vorgegeben ist:** Die komplette grafische Oberfläche (GUI), der Verbindungsaufbau und der Empfangs-Thread.

**Was ihr selbst implementiert:** Das Netzwerkprotokoll und die Spiellogik.

---

## Spielregeln (kurze Zusammenfassung)

- Spielfeld: **10×10** Felder (Spalten A–J, Zeilen 1–10)
- Jeder Spieler hat eine **eigene Flotte**:
  - 1 × Schlachtschiff (Länge 4)
  - 2 × Kreuzer (Länge 3)
  - 3 × Zerstörer (Länge 2)
  - 4 × U-Boot (Länge 1)
- Spieler schießen abwechselnd auf das Feld des Gegners
- Wer zuerst **alle** Schiffe des Gegners versenkt, gewinnt

---

## Arbeitsreihenfolge – Übersicht

```
Schritt 0 │ Tic-Tac-Toe ausprobieren + Code lesen          (zusammen, ~10 min)
Schritt 1 │ Vorlage starten + GUI erkunden                  (zusammen, ~10 min)
Schritt 2 │ Protokoll entwerfen + dokumentieren             (als Team, ~30 min)
          │  └─ PROTOKOLL_ANLEITUNG.md lesen
          │  └─ UNSER_PROTOKOLL.md gemeinsam ausfüllen
──────────┼────────────────────────────────────────────────────────────────────
          │          AB HIER: JEDER PROGRAMMIERT FÜR SICH
──────────┼────────────────────────────────────────────────────────────────────
Schritt 3 │ AUFGABE 1 – Protokoll-Konstanten eintragen      (5 min)
Schritt 4 │ AUFGABE 2 – send_message() implementieren       (10 min)
Schritt 5 │ AUFGABE 8 – on_ready_click() senden             (5 min)
          │  └─ Test: Bereit-Nachricht wird gesendet/empfangen?
Schritt 6 │ AUFGABE 3 – handle_message() implementieren     (20 min)
          │  └─ Test: Spiel startet wenn beide "Fertig" klicken?
Schritt 7 │ AUFGABE 7 – on_shoot() senden                   (5 min)
Schritt 8 │ AUFGABE 4 – process_shot() implementieren       (20 min)
Schritt 9 │ AUFGABE 5 – check_sunk() implementieren         (5 min)
Schritt 10│ AUFGABE 6 – check_all_sunk() implementieren     (5 min)
          │  └─ Test: Komplettes Spiel durchspielen
Schritt 11│ Netzwerktest: zwei Computer                     (10 min)
```

---

## Schritt 0: Tic-Tac-Toe ausprobieren

Startet das fertige Tic-Tac-Toe, um die Netzwerkgrundlage zu verstehen:

```
Terminal 1: python tictactoe_gui_net.py   → wählt "Server"
Terminal 2: python tictactoe_gui_net.py   → wählt "Client" + IP 127.0.0.1
```

Spielt eine Runde und schaut euch dabei den Code an. Achtet besonders auf:
- Wie wird eine Nachricht gesendet? (`send_move`)
- Wie wird eine Nachricht empfangen? (`receive_move`)
- Welches Format hat die Nachricht? (`"row,col"`)

### Dateien im Projekt

| Datei | Beschreibung |
|---|---|
| `tictactoe_gui_net.py` | Das fertige Tic-Tac-Toe als Referenz – zeigt wie alles zusammenspielt |
| `schiffe_versenken_vorlage.py` | **Eure Arbeitsdatei** – hier implementiert ihr das Spiel |
| `ANLEITUNG.md` | Diese Datei |
| `PROTOKOLL_ANLEITUNG.md` | Anleitung zum Protokoll-Entwurf |

---

## Schritt 1: Vorlage starten und GUI erkunden

```
Terminal 1: python schiffe_versenken_vorlage.py   → wählt "Server"
Terminal 2: python schiffe_versenken_vorlage.py   → wählt "Client" + IP 127.0.0.1
```

Die GUI erscheint. Probiert aus:
- Schiffe auf dem linken Feld platzieren (Mausklick)
- Ausrichtung umschalten (Button unten links)
- "Fertig" klicken – **noch nichts passiert**, weil `send_message()` fehlt

### Wo findet ihr eure Aufgaben?

Öffnet `schiffe_versenken_vorlage.py` und sucht nach `❗ AUFGABE`. Ihr findet 8 markierte Stellen.

---

## Schritt 2: Protokoll entwerfen (als ganzes Team!)

**Bevor ihr anfangt zu programmieren**, müsst ihr euch als Team auf ein gemeinsames **Protokoll** einigen!

> Lest dazu **[PROTOKOLL_ANLEITUNG.md](PROTOKOLL_ANLEITUNG.md)** und erstellt gemeinsam eine Datei `UNSER_PROTOKOLL.md`.

Warum ist das so wichtig?  
Spieler 1 (Server) und Spieler 2 (Client) schreiben ihren Code unabhängig voneinander. Wenn sie unterschiedliche Nachrichten verwenden – z.B. einer schreibt `"HIT:3,5"` und der andere erwartet `"TREFFER:3,5"` – versteht keiner den anderen. Das Protokoll ist die gemeinsame Sprache beider Spieler.

**Ergebnis von Schritt 2:** Eine gemeinsam vereinbarte `UNSER_PROTOKOLL.md` mit allen Nachrichten, ihrem Format und der Zuglogik.

---

## Schritt 3: AUFGABE 1 – Protokoll-Konstanten definieren

**Wo:** Ganz oben im Aufgaben-Bereich der Datei `schiffe_versenken_vorlage.py`, bei `❗ AUFGABE 1`

Nachdem ihr in Schritt 2 das Protokoll gemeinsam festgelegt habt, tragt ihr jetzt eure Nachrichten als Konstanten ein.

**Beispiel** (ihr könnt andere Namen/Formate wählen):

```python
MSG_READY = "FERTIG"       # Spieler hat alle Schiffe gesetzt und ist bereit
MSG_SHOOT = "SCHUSS"       # Schuss abgefeuert (Parameter: Zeile,Spalte)
MSG_HIT   = "TREFFER"      # Schuss hat getroffen (Parameter: Zeile,Spalte)
MSG_MISS  = "WASSER"       # Schuss hat daneben getroffen (Parameter: Zeile,Spalte)
MSG_SUNK  = "VERSENKT"     # Ein Schiff wurde vollständig versenkt
MSG_WIN   = "VERLOREN"     # Alle eigenen Schiffe versenkt → Gegner hat gewonnen
```

> ⚠️ **Wichtig:** Beide Spieler müssen **exakt dieselben** Konstanten verwenden!

---

## Schritt 4: AUFGABE 2 – Nachrichten senden

**Wo:** Funktion `send_message(msg)` bei `❗ AUFGABE 2`

### Was macht diese Funktion?

Nachrichten werden als Text-String übergeben und müssen über das Netzwerk gesendet werden. Netzwerke können nur **Bytes** übertragen, keine Python-Strings. Deshalb brauchen wir `.encode()`.

Außerdem hängt die Funktion `"\n"` ans Ende. Warum? Der Empfänger liest zeilenweise. Das `"\n"` zeigt: "Hier ist die Nachricht fertig."

### Lösung

```python
def send_message(msg):
    global conn
    try:
        conn.sendall((msg + "\n").encode())
        print(f"[GESENDET] {msg}")
    except Exception as e:
        print(f"[FEHLER beim Senden] {e}")
```

### Testen

Diese Funktion allein ist noch nicht testbar – macht direkt weiter mit Schritt 5 (AUFGABE 8), danach könnt ihr testen:

1. Starte beide Instanzen
2. Platziere alle Schiffe (linkes Feld, Mausklick)
3. Klicke "Fertig"
4. Überprüft im Terminal: erscheint `[GESENDET] FERTIG` (oder eure Nachricht)?
5. Auf der anderen Seite: erscheint `[EMPFANGEN] FERTIG`?

---

## Schritt 5: AUFGABE 8 – Bereit melden

**Wo:** Funktion `on_ready_click()` bei `❗ AUFGABE 8`

Wenn "Fertig" geklickt wird, muss der Gegner informiert werden:

```python
def on_ready_click():
    global i_am_ready, game_phase
    # ... (bestehender Code bleibt)
    
    # ❗ Eure Zeile:
    send_message(MSG_READY)
    
    check_both_ready()
```

### Testen nach Schritt 4 + 5

1. Starte beide Instanzen
2. Platziere alle Schiffe (linkes Feld, Mausklick)
3. Klicke "Fertig"
4. Terminal prüfen: erscheint `[GESENDET] FERTIG` (oder eure Nachricht)?
5. Auf der anderen Seite: erscheint `[EMPFANGEN] FERTIG`?

Wenn das klappt, funktioniert die Netzwerkverbindung grundsätzlich!

---

## Schritt 6: AUFGABE 3 – Nachrichten empfangen und verarbeiten

> 📚 **Neue Python-Konzepte in dieser Aufgabe?**
> Diese Aufgabe nutzt `split()`, `map()`, Mehrfachzuweisungen, `if/elif/else` und Funktionsaufrufe mit Rückgabewert.
> → [**Python-Übungsseite öffnen**](python_uebungen.html) – mit Erklärungen und Übungsaufgaben zu allen nötigen Grundlagen.

Das ist **die wichtigste Aufgabe**. Die Funktion `handle_message(msg)` reagiert auf alle eingehenden Nachrichten.

**Wo:** Funktion `handle_message(msg)` bei `❗ AUFGABE 3`

### Testen nach Schritt 6

Nach Schritt 6 sollte das Spiel starten wenn beide "Fertig" klicken. Schießen klappt noch nicht (Schritt 7 fehlt).

### Welche Nachrichten müsst ihr verarbeiten?

| Erhaltene Nachricht | Was passiert? |
|---|---|
| `"FERTIG"` | Gegner ist bereit → `opponent_ready = True` → `check_both_ready()` |
| `"SCHUSS:3,5"` | Gegner schießt auf (3,5) → `process_shot(3, 5)` aufrufen |
| `"TREFFER:3,5"` | Euer Schuss hat getroffen → Gegnerfeld markieren → nächster Zug |
| `"WASSER:3,5"` | Euer Schuss hat verfehlt → Gegnerfeld markieren → Gegner dran |
| `"VERSENKT"` | Eines eurer Schiffe wurde versenkt → Meldung anzeigen |
| `"VERLOREN"` | Alle Schiffe des Gegners versenkt → ihr habt gewonnen! |

### Nachrichten aufteilen

Nachrichten haben das Format `BEFEHL:PARAMETER`. Teilt sie mit `.split(":")` auf:

```python
msg = "SCHUSS:3,5"
teile = msg.split(":")
befehl = teile[0]           # → "SCHUSS"
parameter = teile[1]        # → "3,5"
row, col = map(int, parameter.split(","))  # → row=3, col=5
```

### Lösung (Grundstruktur)

```python
def handle_message(msg):
    global opponent_ready

    print(f"[EMPFANGEN] {msg}")

    teile = msg.split(":")
    befehl = teile[0]

    if befehl == MSG_READY:
        opponent_ready = True
        check_both_ready()

    elif befehl == MSG_SHOOT:
        row, col = map(int, teile[1].split(","))
        process_shot(row, col)

    elif befehl == MSG_HIT:
        row, col = map(int, teile[1].split(","))
        mark_enemy_hit(row, col)
        switch_to_my_turn()       # Treffer → nochmals schießen? Ihr entscheidet!

    elif befehl == MSG_MISS:
        row, col = map(int, teile[1].split(","))
        mark_enemy_miss(row, col)
        switch_to_opponent_turn() # Verfehlt → Gegner ist dran

    elif befehl == MSG_SUNK:
        update_status("💥 Eines deiner Schiffe wurde versenkt!")

    elif befehl == MSG_WIN:
        end_game(i_won=True)      # Gegner meldet "VERLOREN" → ich habe gewonnen!
```

> 💡 **Hinweis zum Treffer:** In klassischem Schiffe Versenken darf man nach einem Treffer **nochmals schießen**. Entscheidet ihr euch dafür, ändert sich die Zugslogik! Überlegt im Team was sinnvoll ist und haltet es im Protokolldokument fest.

---

## Schritt 7: AUFGABE 7 – Schuss abschicken

**Wo:** Funktion `on_shoot(row, col)` bei `❗ AUFGABE 7`

Wenn der Spieler auf das Gegnerfeld klickt, soll eine Schuss-Nachricht gesendet werden.

### Testen nach Schritt 7

Jetzt sollte ein Klick auf das Gegnerfeld eine Nachricht senden. Im Terminal erscheint `[GESENDET] SCHUSS:x,y`. Der Gegner empfängt sie, kann aber noch nicht reagieren (Schritt 8 fehlt).

```python
def on_shoot(row, col):
    global is_my_turn, game_phase
    is_my_turn = False
    game_phase = "WAITING_FOR_RESULT"
    enemy_canvas.unbind("<Button-1>")
    update_status(f"💣 Schuss auf {chr(65 + col)}{row + 1}! Warte auf Ergebnis...")

    # ❗ Eure Zeile:
    send_message(f"{MSG_SHOOT}:{row},{col}")
```

---

## Schritt 8: AUFGABE 4 – Schuss des Gegners verarbeiten

**Wo:** Funktion `process_shot(row, col)` bei `❗ AUFGABE 4`

Wenn der Gegner schießt, müsst ihr:

1. Prüfen ob er getroffen hat (`my_grid[row][col] == SHIP`)
2. Euer Spielfeld aktualisieren
3. Dem Gegner das Ergebnis schicken
4. Prüfen ob ein Schiff oder alle Schiffe versenkt wurden

### Lösung

```python
def process_shot(row, col):
    if my_grid[row][col] == SHIP:
        # Treffer!
        mark_my_hit(row, col)

        # Welches Schiff wurde getroffen?
        getroffenes_schiff = None
        for schiff in my_ships:
            if (row, col) in schiff:
                getroffenes_schiff = schiff
                break

        if check_sunk(getroffenes_schiff):
            # Schiff versenkt!
            send_message(MSG_SUNK)
            if check_all_sunk():
                # Alle Schiffe versenkt → ich habe verloren
                send_message(MSG_WIN)
                end_game(i_won=False)
                return
            else:
                # Weiter machen – Gegner trifft nochmal (falls Treffer = nochmal)
                send_message(f"{MSG_HIT}:{row},{col}")
        else:
            send_message(f"{MSG_HIT}:{row},{col}")

        # Entscheidung: Treffer = Gegner dran oder nochmals schießen?
        switch_to_opponent_turn()   # oder switch_to_my_turn() je nach eurer Regel!

    else:
        # Verfehlt
        mark_my_miss(row, col)
        send_message(f"{MSG_MISS}:{row},{col}")
        switch_to_my_turn()         # Ich bin wieder dran
```

> ⚠️ **Achtung:** Die Reihenfolge der `switch_to_*_turn()` Aufrufe und die Regel "nach Treffer nochmals schießen" **müsst ihr mit eurem Protokolldokument abgleichen**! Beide Spieler müssen dieselbe Logik haben.

---

## Schritt 9: AUFGABE 5 – check_sunk() implementieren

**Wo:** Funktion `check_sunk(ship_cells)` bei `❗ AUFGABE 5`

Prüft ob alle Zellen eines Schiffes den Zustand `HIT` haben:

```python
def check_sunk(ship_cells):
    return all(my_grid[r][c] == HIT for (r, c) in ship_cells)
```

---

## Schritt 10: AUFGABE 6 – check_all_sunk() implementieren

**Wo:** Funktion `check_all_sunk()` bei `❗ AUFGABE 6`

Prüft ob alle Schiffe in `my_ships` vollständig versenkt sind:

```python
def check_all_sunk():
    return all(check_sunk(schiff) for schiff in my_ships)
```

### Testen nach Schritten 8–10

Jetzt sollte ein komplettes Spiel durchgespielt werden können! Spielt lokal auf einem Computer (IP `127.0.0.1`) und prüft:
- Schüsse landen auf dem richtigen Feld?
- Treffer/Wasser wird korrekt angezeigt?
- Spiel endet wenn alle Schiffe versenkt sind?

---

## Schritt 11: Netzwerktest – zwei Computer

1. Findet die IP-Adresse des Server-Computers:  
   Windows: Eingabeaufforderung öffnen → `ipconfig` eingeben  
   → Sucht bei "IPv4-Adresse" z.B. `192.168.1.42`

2. Stellt sicher, dass beide Computer im **gleichen Netzwerk** (WLAN/LAN) sind

3. Möglicherweise muss die **Firewall** Port 65432 freigeben (fragt euren Lehrer)

---

## Debugging-Tipps

### Lokaler Test (ein Computer, für alle Schritte)

```
Terminal 1: python schiffe_versenken_vorlage.py  → Server
Terminal 2: python schiffe_versenken_vorlage.py  → Client, IP: 127.0.0.1
```

`127.0.0.1` ist die sogenannte **Loopback-Adresse** – der Computer verbindet sich mit sich selbst.

### Print-Ausgaben nutzen

Die `print()`-Ausgaben im Terminal helfen euch:
- `[GESENDET] ...` – Was ihr gesendet habt
- `[EMPFANGEN] ...` – Was ihr empfangen habt

Wenn das Spiel "hängt":
- Schaut im Terminal nach ob Nachrichten gesendet/empfangen werden
- Prüft ob der Befehlsname in `handle_message()` exakt mit eurer Konstante übereinstimmt
- Groß-/Kleinschreibung beachten! `"FERTIG" != "fertig"`

### Häufige Fehler

| Problem | Mögliche Ursache |
|---|---|
| Verbindung wird nicht hergestellt | Falsche IP-Adresse / Firewall blockiert Port 65432 |
| Spiel startet nicht nach "Fertig" | `MSG_READY` wird nicht korrekt gesendet oder empfangen |
| Schuss kommt nicht an | `MSG_SHOOT` in `on_shoot()` vergessen zu implementieren |
| Treffer/Verfehlt wird falsch angezeigt | Falsche `mark_*()` Funktion aufgerufen |
| Spiel endet nicht | `check_all_sunk()` gibt immer `False` zurück (Platzhalter!) |

---

## Erweiterungsideen (für Schnelle)

Falls ihr früher fertig seid:

1. **Zeitanzeige**: Wie lange dauert ein Spiel? (Nutzt `time.time()`)
2. **Schiff-Koordinaten beim Versenken anzeigen**: Wenn ein Schiff versenkt wird, markiert alle seine Felder auf dem Gegnerfeld
3. **Neustart**: Nach Spielende einen "Nochmal spielen"-Button anbieten
4. **Chat**: Eine Nachrichtenfunktion zwischen den Spielern einbauen
5. **Statistik**: Wie viele Schüsse hat jeder Spieler gebraucht?

---

## Wichtige Konzepte zum Nachschlagen

### Client-Server-Modell

```
Server (wartet)          Client (verbindet sich)
─────────────────        ─────────────────────────
sock.bind(port)  ←──     
sock.listen()    ←──     
conn = sock.accept() ←── sock.connect(ip, port)
         ↕                        ↕
    conn.send()          conn.recv()
    conn.recv()          conn.send()
```

### Threading

```python
# Ohne Thread: GUI friert ein während auf Netzwerk gewartet wird!
# Mit Thread: GUI bleibt reaktionsfähig

def receive_loop():
    while True:
        data = conn.recv(1024)   # Blockiert bis Daten kommen
        handle_message(data)     # Verarbeite Nachricht

# Thread im Hintergrund starten:
threading.Thread(target=receive_loop, daemon=True).start()
# daemon=True → Thread endet automatisch mit dem Hauptprogramm
```

### String zu Bytes und zurück

```python
# Senden: String → Bytes
nachricht = "SCHUSS:3,5"
conn.sendall((nachricht + "\n").encode())   # encode() = String → Bytes

# Empfangen: Bytes → String
data = conn.recv(1024)         # empfängt Bytes
text = data.decode().strip()   # decode() = Bytes → String, strip() = \n entfernen
```
