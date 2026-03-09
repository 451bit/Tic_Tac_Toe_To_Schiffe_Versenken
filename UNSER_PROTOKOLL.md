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
