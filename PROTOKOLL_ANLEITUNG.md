# Protokollentwurf – Anleitung für Schüler

## Was ist ein Netzwerkprotokoll?

Wenn zwei Computer miteinander kommunizieren, müssen sie eine gemeinsame Sprache sprechen. Diese Sprache heißt **Protokoll**. Ein Protokoll legt fest:

- **Welche Nachrichten** es gibt (z.B. "Schuss", "Treffer", "Verfehlt")
- **Welches Format** jede Nachricht hat (z.B. `SCHUSS:3,5`)
- **Wann** welche Nachricht gesendet wird (z.B. nur wenn ich dran bin)
- **Was der Empfänger** mit der Nachricht tun soll

Bekannte Protokolle im Alltag:
- **HTTP** – Webseiten abrufen (`GET /index.html`)
- **SMTP** – E-Mails versenden (`MAIL FROM: ...`)
- **DNS** – Domainnamen auflösen (`google.com → 142.250.185.46`)

In diesem Projekt entwerft ihr euer **eigenes Protokoll** für Schiffe Versenken.

---

## Warum ist das Protokoll so wichtig?

Spieler 1 (Server) und Spieler 2 (Client) programmieren unabhängig voneinander. Beide schreiben:
- Eine `send_message()` Funktion (Nachricht senden)
- Eine `handle_message()` Funktion (Nachricht empfangen und reagieren)

**Wenn das Protokoll nicht übereinstimmt, funktioniert das Spiel nicht!**

Beispiel für ein Problem:

```
Spieler 1 sendet:    "HIT:3,5"
Spieler 2 erwartet:  "TREFFER:3,5"
→ Spieler 2 versteht die Nachricht nicht → Spiel hängt!
```

Deshalb: **Zuerst Protokoll festlegen, dann erst programmieren.**

---

## Phase 1: Spielablauf analysieren

Bevor ihr Nachrichten definiert, müsst ihr den Spielablauf kennen. Geht jeden Schritt durch und fragt euch: **Was muss hier über das Netzwerk kommuniziert werden?**

### Spielphasen

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: VERBINDUNG AUFBAUEN                           │
│  Server startet → wartet auf Client                     │
│  Client verbindet sich                                  │
│  → Kein Protokoll nötig (übernimmt das Betriebssystem)  │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: SCHIFFE SETZEN                                │
│  Beide Spieler setzen ihre Schiffe (lokal, kein Netz)   │
│  Wenn fertig: Spieler drückt "Fertig"                   │
│  → Nachricht: "Ich bin bereit!"                         │
│  Beide warten bis der andere auch fertig ist            │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: SPIELPHASE (abwechselnd)                      │
│  Spieler A schießt → sendet Schuss-Koordinaten          │
│  Spieler B prüft sein Feld → sendet Ergebnis zurück     │
│  (Treffer oder Verfehlt)                                │
│  Falls Treffer: Schiff versenkt? Alle versenkt?         │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: SPIELENDE                                     │
│  Ein Spieler hat alle Schiffe des Gegners versenkt      │
│  → Nachricht: "Ich habe verloren" (oder "Du hast gewonnen")│
└─────────────────────────────────────────────────────────┘
```

---

## Phase 2: Nachrichten identifizieren

Geht jede Phase durch und listet auf, welche Nachrichten gesendet werden müssen.

### Aufgabe: Füllt diese Tabelle aus

| Ereignis | Wer sendet? | Was wird gesendet? | Welche Daten braucht der Empfänger? |
|---|---|---|---|
| "Ich bin bereit" | Beide | ? | Keine (reicht ein Signal) |
| Schuss abgefeuert | Angreifer | ? | Zeile und Spalte |
| Schuss trifft Schiff | Verteidiger | ? | ? |
| Schuss trifft Wasser | Verteidiger | ? | ? |
| Schiff vollständig versenkt | Verteidiger | ? | ? (Position, Größe, Richtung?) |
| Alle Schiffe versenkt (verloren) | Verteidiger | ? | ? |

---

## Phase 3: Nachrichtenformat festlegen

Ihr müsst entscheiden wie eine Nachricht aussieht. Zwei Dinge braucht jede Nachricht:

1. **Befehlsname** – Was passiert? (z.B. `SCHUSS`, `TREFFER`)
2. **Parameter** – Zusätzliche Informationen (z.B. Zeile und Spalte)

### Empfohlenes Format: `BEFEHL:PARAMETER`

Der Doppelpunkt trennt den Befehlsnamen vom Parameter. Mehrere Parameter werden durch Komma getrennt.

```
Nur Befehl:          FERTIG
Befehl + 1 Parameter: VERSENKT:4
Befehl + 2 Parameter: SCHUSS:3,5
Befehl + 4 Parameter: SCHIFF:3,5,3,H     (Zeile, Spalte, Länge, Richtung)
```

Auf der Empfängerseite wird aufgeteilt:
```python
teile   = "SCHUSS:3,5".split(":")    # → ["SCHUSS", "3,5"]
befehl  = teile[0]                   # → "SCHUSS"
row, col = map(int, teile[1].split(","))  # → 3, 5
```

### Alternative Formate (nicht empfohlen für Anfänger)

| Format | Beispiel | Vor-/Nachteile |
|---|---|---|
| Leerzeichen-getrennt | `SCHUSS 3 5` | Einfach, aber unübersichtlich bei vielen Parametern |
| JSON | `{"cmd":"SCHUSS","row":3,"col":5}` | Sehr flexibel, aber aufwendiger zu parsen |
| Komma-getrennt | `SCHUSS,3,5` | Kompakt, aber Befehlsname ist schwerer zu extrahieren |

---

## Phase 4: Zuglogik klären

**Wichtige Designentscheidung:** Darf man nach einem Treffer nochmals schießen?

### Option A: Treffer = nochmals schießen (klassische Regel)

```
Spieler A schießt → Treffer → Spieler A schießt nochmal
Spieler A schießt → Verfehlt → Spieler B ist dran
```

**Ablauf über Netzwerk:**
```
A → B: "SCHUSS:3,5"
B → A: "TREFFER:3,5"     (A schießt nochmal)
A → B: "SCHUSS:4,5"
B → A: "WASSER:4,5"      (B ist jetzt dran)
B → A: "SCHUSS:7,2"
A → B: "TREFFER:7,2"     (B schießt nochmal)
...
```

### Option B: Immer abwechseln (vereinfachte Regel)

```
Spieler A schießt → egal ob Treffer oder Miss → Spieler B ist dran
```

**Ablauf über Netzwerk:**
```
A → B: "SCHUSS:3,5"
B → A: "TREFFER:3,5"     (trotzdem: B ist jetzt dran)
B → A: "SCHUSS:7,2"
A → B: "TREFFER:7,2"     (trotzdem: A ist jetzt dran)
...
```

> **Unsere Empfehlung:** Startet mit **Option B** (einfacher). Wenn alles funktioniert, könnt ihr Option A einbauen.

---

## Phase 5: Protokolldokument erstellen

Erstellt gemeinsam eine Datei `UNSER_PROTOKOLL.md` und füllt diese Vorlage aus:

---

### Vorlage: UNSER_PROTOKOLL.md

```markdown
# Protokoll: Schiffe Versenken Netzwerkspiel

## Übersicht

**Gruppe:** [Namen der Gruppe]  
**Datum:** [Datum]  
**Version:** 1.0

---

## Allgemeines

- **Trennzeichen:** Doppelpunkt `:` zwischen Befehl und Parametern
- **Parametertrennzeichen:** Komma `,` zwischen mehreren Parametern
- **Zeilenende:** Jede Nachricht endet mit `\n` (newline)
- **Zeichenkodierung:** UTF-8

---

## Nachrichten-Übersicht

| Konstante  | Nachricht | Parameter | Wann gesendet |
|---|---|---|---|
| MSG_READY  | `FERTIG` | keine | Wenn alle Schiffe gesetzt und "Fertig" geklickt |
| MSG_SHOOT  | `SCHUSS` | `zeile,spalte` | Wenn Spieler auf Gegnerfeld klickt |
| MSG_HIT    | `TREFFER` | `zeile,spalte` | Wenn Schuss ins Schwarze trifft |
| MSG_MISS   | `WASSER` | `zeile,spalte` | Wenn Schuss Wasser trifft |
| MSG_SUNK   | `VERSENKT` | keine | Wenn Schiff vollständig versenkt |
| MSG_WIN    | `VERLOREN` | keine | Wenn alle eigenen Schiffe versenkt |

---

## Detailbeschreibung

### FERTIG (Bereit-Signal)

- **Format:** `FERTIG\n`
- **Gesendet von:** Beiden Spielern (unabhängig)
- **Parameter:** keine
- **Reaktion des Empfängers:**
  - `opponent_ready = True` setzen
  - Prüfen ob auch ich bereit bin (`check_both_ready()`)
  - Wenn beide bereit: Spiel starten

---

### SCHUSS (Schuss abfeuern)

- **Format:** `SCHUSS:zeile,spalte\n`
- **Gesendet von:** Dem Spieler der gerade dran ist
- **Parameter:**
  - `zeile`: 0–9 (entspricht Zeilen 1–10 auf dem Spielfeld)
  - `spalte`: 0–9 (entspricht Spalten A–J auf dem Spielfeld)
- **Beispiel:** `SCHUSS:3,5` → Schuss auf Feld F4 (Spalte 5=F, Zeile 3+1=4)
- **Reaktion des Empfängers:**
  - `process_shot(zeile, spalte)` aufrufen
  - Antworten mit TREFFER oder WASSER

---

### TREFFER (Schuss hat getroffen)

- **Format:** `TREFFER:zeile,spalte\n`
- **Gesendet von:** Dem Spieler dessen Feld beschossen wurde
- **Parameter:** Dieselbe Zeile/Spalte wie beim SCHUSS
- **Reaktion des Empfängers (Angreifer):**
  - `mark_enemy_hit(zeile, spalte)` aufrufen
  - [Entscheidung: nochmals schießen oder Gegner dran?]

---

### WASSER (Schuss hat verfehlt)

- **Format:** `WASSER:zeile,spalte\n`
- **Gesendet von:** Dem Spieler dessen Feld beschossen wurde
- **Parameter:** Dieselbe Zeile/Spalte wie beim SCHUSS
- **Reaktion des Empfängers (Angreifer):**
  - `mark_enemy_miss(zeile, spalte)` aufrufen
  - Gegner ist jetzt dran (`switch_to_opponent_turn()`)

---

### VERSENKT (Schiff vollständig versenkt)

- **Format:** `VERSENKT\n`  (oder `VERSENKT:zeile1,spalte1,...` mit Koordinaten)
- **Gesendet von:** Dem Spieler dessen Schiff versenkt wurde
- **Wann:** Nachdem TREFFER bestätigt wurde UND Schiff vollständig versenkt
- **Reaktion:** Status-Meldung anzeigen

---

### VERLOREN (Alle Schiffe versenkt)

- **Format:** `VERLOREN\n`
- **Gesendet von:** Dem Spieler dessen alle Schiffe versenkt wurden
- **Wann:** Wenn `check_all_sunk()` = True
- **Reaktion des Empfängers:**
  - `end_game(i_won=True)` aufrufen (Empfänger hat gewonnen)
- **Eigene Reaktion (Sender):**
  - `end_game(i_won=False)` aufrufen (ich habe verloren)

---

## Sequenzdiagramm (Spielphase)

```
Spieler A (Server)           Spieler B (Client)
       │                             │
       │──── SCHUSS:3,5 ────────────>│  A schießt auf B's Feld (3,5)
       │                             │  B prüft: Treffer!
       │<─── TREFFER:3,5 ───────────│  B antwortet
       │                             │
       │  [A darf nochmals schießen  │
       │     ODER B ist dran –       │
       │     gemäß unserer Regel!]   │
       │                             │
       │──── SCHUSS:7,2 ────────────>│  A schießt nochmal (falls Regel: Treffer → nochmal)
       │                             │  B prüft: Wasser!
       │<─── WASSER:7,2 ────────────│  B antwortet
       │                             │
       │                             │──── SCHUSS:5,3 ────>  (B ist jetzt dran)
       ...
```

---

## Zusatznachrichten (optional, für Erweiterungen)

| Konstante | Nachricht | Beschreibung |
|---|---|---|
| MSG_CHAT | `CHAT:text` | Chatnachricht zwischen Spielern |
| MSG_SURRENDER | `AUFGEBEN` | Spieler gibt auf |

---

## Versionsverlauf

| Version | Änderungen |
|---|---|
| 1.0 | Initiales Protokoll |
```

---

## Checkliste: Protokoll fertig?

Bevor ihr anfangt zu programmieren, checkt folgendes ab:

- [ ] Alle Spielphasen abgedeckt?
- [ ] Jede mögliche Nachricht definiert?
- [ ] Format und Trennzeichen festgelegt?
- [ ] Zuglogik bei Treffer entschieden (nochmals schießen oder nicht)?
- [ ] Was passiert wenn Verbindung abbricht? (für Fortgeschrittene)
- [ ] Beide Spieler haben das Protokolldokument?
- [ ] Alle Konstanten-Namen abgestimmt?

---

## Häufige Protokollfehler

### Fehler 1: Unterschiedliche Befehlsnamen

```
Spieler 1 sendet:    "SHOOT:3,5"
Spieler 2 erwartet:  "SCHUSS:3,5"
→ Nachricht wird ignoriert, Spiel hängt
```
**Lösung:** Exakt dieselben Zeichenketten in beiden Programmen verwenden.

### Fehler 2: Falsche Parameter-Reihenfolge

```
Spieler 1 sendet:    "SCHUSS:spalte,zeile"   (erst Spalte, dann Zeile)
Spieler 2 erwartet:  "SCHUSS:zeile,spalte"   (erst Zeile, dann Spalte)
→ Schüsse landen auf falschen Feldern
```
**Lösung:** Reihenfolge explizit im Protokolldokument festhalten.

### Fehler 3: Vergessener Zeilenwechsel

```python
conn.sendall("FERTIG".encode())   # Fehlt: + "\n"
```
Empfänger liest mit `readline()` – ohne `\n` wartet er ewig.  
**Lösung:** Immer `"\n"` ans Ende hängen!

### Fehler 4: Falscher Spielzug nach Treffer/Verfehlt

```
A schießt → B sagt "TREFFER" → A denkt "Gegner ist jetzt dran" → wartet
B denkt "A schießt nochmal" → wartet auch
→ Beide warten, Deadlock!
```
**Lösung:** Zugregeln (wer nach Treffer/Verfehlt dran ist) **exakt** im Protokoll festlegen.
