"""
Schiffe Versenken - Netzwerkspiel
===================================
VORLAGE FÜR SCHÜLER – Klasse 11

Das Projekt:
    Zwei Spieler verbinden sich über das lokale Netzwerk und spielen Schiffe Versenken.

Spielfeld: 10×10 Felder (Spalten A–J, Zeilen 1–10)

Flotte (jeder Spieler):
    1 × Schlachtschiff  (Länge 4)
    2 × Kreuzer         (Länge 3)
    3 × Zerstörer       (Länge 2)
    4 × U-Boot          (Länge 1)
    ─────────────────────────────
    Gesamt: 20 Felder

Spielregeln (klassisch):
    - Spieler abwechselnd schießen
    - Treffer → nochmal schießen (Bonus-Regel, selbst entscheiden!)
    - Wer zuerst alle Schiffe des Gegners versenkt, gewinnt

Was ist VORGEGEBEN (nicht verändern):
    ✅ Die komplette grafische Oberfläche (GUI)
    ✅ Das Schiffe-Platzieren mit Maus + Vorschau
    ✅ Der Verbindungsaufbau (Server/Client)
    ✅ Der Empfangs-Thread (Nachrichten kommen automatisch an)
    ✅ Hilfsfunktionen: mark_*(), switch_to_*(), end_game(), ...

Was IHR implementieren müsst (sucht nach "❗ AUFGABE"):
    ❗ AUFGABE 1: Protokoll-Konstanten definieren
    ❗ AUFGABE 2: send_message() – Nachricht über Netzwerk senden
    ❗ AUFGABE 3: handle_message() – Nachricht empfangen + reagieren
    ❗ AUFGABE 4: process_shot() – Schuss des Gegners verarbeiten
    ❗ AUFGABE 5: check_sunk() – Prüfen ob ein Schiff versenkt wurde
    ❗ AUFGABE 6: check_all_sunk() – Prüfen ob alle Schiffe versenkt
    ❗ AUFGABE 7: on_shoot() vervollständigen – Schuss abschicken
    ❗ AUFGABE 8: on_ready_click() vervollständigen – Bereit melden
"""

import sys
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox


# ============================================================================
# KONSTANTEN (nicht verändern!)
# ============================================================================

PORT      = 65432   # Netzwerk-Port (wie eine "Tür-Nummer", 0–1023 sind reserviert)
GRID_SIZE = 10      # 10×10 Spielfeld
CELL_SIZE = 40      # Größe einer Zelle in Pixeln

# Zellzustände – was kann eine einzelne Zelle enthalten?
EMPTY = 0   # Leeres Wasser / noch nicht beschossen
SHIP  = 1   # Eigenes Schiff (nur auf dem eigenen Feld)
HIT   = 2   # Getroffen!
MISS  = 3   # Daneben (nur Wasser getroffen)

# Farben für die Darstellung der Zellen
COLORS = {
    "water"  : "#87CEEB",   # Hellblau  = unbekanntes Wasser
    "ship"   : "#5D6D7E",   # Grau      = eigenes Schiff
    "hit"    : "#C0392B",   # Rot       = Treffer
    "miss"   : "#BDC3C7",   # Hellgrau  = Verfehlt
    "grid"   : "#1A5276",   # Dunkelblau = Gitterlinien
    "preview": "#82E0AA",   # Hellgrün  = Schiff-Vorschau (gültige Position)
    "invalid": "#F1948A",   # Hellrot   = Schiff-Vorschau (ungültige Position)
    "label"  : "#1A5276",   # Dunkelblau = Buchstaben/Zahlen-Beschriftung
}

# Die Flotte: Liste von (anzahl, länge)
# Insgesamt: 1×4 + 2×3 + 3×2 + 4×1 = 20 Felder
FLEET = [
    (1, 4),   # 1 Schlachtschiff
    (2, 3),   # 2 Kreuzer
    (3, 2),   # 3 Zerstörer
    (4, 1),   # 4 U-Boote
]


# ============================================================================
# GLOBALE VARIABLEN – Spielzustand
# ============================================================================

# Eigenes Spielfeld (10×10)
# Mögliche Werte: EMPTY, SHIP, HIT, MISS
my_grid = [[EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]

# Gegnerisches Spielfeld aus unserer Sicht (10×10)
# Werte: EMPTY = noch nicht beschossen, HIT = wir haben getroffen, MISS = wir haben verfehlt
enemy_grid = [[EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]

# Eigene Schiffe – Liste von Schiffen
# Jedes Schiff ist eine Liste von (row, col) Tupeln
# Beispiel: [(0,0),(0,1),(0,2)] = horizontales 3er-Schiff in Zeile 0, Spalten 0–2
my_ships = []

# Noch nicht gesetzte Schiffsgrößen (wird aus FLEET befüllt)
# Beispiel: [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
pending_ships = []

# ---- Platzierungsphase ----
placing_h = True        # Ausrichtung: True = horizontal, False = vertikal

# ---- Spielsteuerung ----
my_role         = ""      # "server" oder "client"
game_phase      = "PLACING"   # Aktueller Spielstatus
is_my_turn      = False   # Bin ich gerade dran?
i_am_ready      = False   # Habe ich auf "Fertig" gedrückt?
opponent_ready  = False   # Hat der Gegner "Fertig" gedrückt?


# ============================================================================
# GLOBALE VARIABLEN – Netzwerk
# ============================================================================

sock = None   # Das Socket-Objekt (für Verbindungsaufbau)
conn = None   # Die aktive bidirektionale Verbindung zum Gegner


# ============================================================================
# GLOBALE VARIABLEN – GUI-Elemente
# (werden in create_gui() gesetzt, hier nur vordeklariert)
# ============================================================================

root          = None   # Hauptfenster
status_label  = None   # Statusanzeige oben
my_canvas     = None   # Canvas für das eigene Spielfeld (links)
enemy_canvas  = None   # Canvas für das gegnerische Spielfeld (rechts)
btn_direction = None   # Schaltfläche: Ausrichtung umschalten
btn_ready     = None   # Schaltfläche: "Fertig" / Bereit
fleet_label   = None   # Anzeige: noch zu setzende Schiffe


# ============================================================================
# GUI-HILFSFUNKTIONEN (VORGEGEBEN – nicht verändern!)
# ============================================================================

def update_status(text):
    """
    Aktualisiert den Statustext oben im Fenster.
    Kann sicher aus jedem Thread aufgerufen werden.
    """
    if status_label and root:
        root.after(0, lambda t=text: status_label.config(text=t))


def draw_grid(canvas, grid, show_ships):
    """
    Zeichnet ein 10×10 Spielfeld auf den angegebenen Canvas.

    Parameter:
        canvas:     tk.Canvas auf dem gezeichnet wird
        grid:       2D-Liste (10×10) mit den Zellwerten
        show_ships: True  → Schiffe (SHIP) als graue Zellen zeigen (eigenes Feld)
                    False → Schiffspositionen des Gegners verstecken
    """
    canvas.delete("all")

    # Spaltenbeschriftung: A B C D E F G H I J
    for c in range(GRID_SIZE):
        x = c * CELL_SIZE + CELL_SIZE + CELL_SIZE // 2
        canvas.create_text(x, CELL_SIZE // 2,
                           text=chr(65 + c),
                           font=("Arial", 10, "bold"),
                           fill=COLORS["label"])

    # Zeilenbeschriftung: 1 2 3 … 10
    for r in range(GRID_SIZE):
        y = r * CELL_SIZE + CELL_SIZE + CELL_SIZE // 2
        canvas.create_text(CELL_SIZE // 2, y,
                           text=str(r + 1),
                           font=("Arial", 10, "bold"),
                           fill=COLORS["label"])

    # Spielfeld-Zellen zeichnen
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x1 = c * CELL_SIZE + CELL_SIZE
            y1 = r * CELL_SIZE + CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            cell_value = grid[r][c]

            # Farbe anhand des Zellwerts bestimmen
            if cell_value == HIT:
                color = COLORS["hit"]
            elif cell_value == MISS:
                color = COLORS["miss"]
            elif cell_value == SHIP and show_ships:
                color = COLORS["ship"]
            else:
                color = COLORS["water"]  # EMPTY oder unbekannter Gegner-Bereich

            # Rechteck (Zelle) zeichnen
            canvas.create_rectangle(x1, y1, x2, y2,
                                    fill=color,
                                    outline=COLORS["grid"],
                                    width=1)

            # Symbole auf getroffene / verfehlte Zellen
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if cell_value == HIT:
                canvas.create_text(cx, cy, text="✕",
                                   font=("Arial", 14, "bold"),
                                   fill="white")
            elif cell_value == MISS:
                canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                   fill="#888888", outline="")


def draw_my_grid():
    """Zeichnet das eigene Spielfeld neu (Schiffe sichtbar)."""
    if my_canvas and root:
        root.after(0, lambda: draw_grid(my_canvas, my_grid, show_ships=True))


def draw_enemy_grid():
    """Zeichnet das gegnerische Spielfeld neu (Schiffe versteckt)."""
    if enemy_canvas and root:
        root.after(0, lambda: draw_grid(enemy_canvas, enemy_grid, show_ships=False))


def update_fleet_label():
    """Aktualisiert die Anzeige der noch zu platzierenden Schiffe."""
    if not fleet_label:
        return
    if not pending_ships:
        fleet_label.config(text="✅ Alle Schiffe gesetzt!", fg="green")
    else:
        counts = {}
        for s in pending_ships:
            counts[s] = counts.get(s, 0) + 1
        lines = ["Noch zu setzen:"]
        for size in sorted(counts.keys(), reverse=True):
            bar = "█" * size
            lines.append(f"  {bar}  (Länge {size}): noch {counts[size]}×")
        fleet_label.config(text="\n".join(lines), fg="black")


# ============================================================================
# SCHIFFS-PLATZIERUNG (VORGEGEBEN – nicht verändern!)
# ============================================================================

def get_ship_cells(row, col, size, horizontal):
    """Gibt die Zellpositionen eines Schiffs als Liste von (row, col) zurück."""
    if horizontal:
        return [(row, col + i) for i in range(size)]
    else:
        return [(row + i, col) for i in range(size)]


def is_valid_placement(cells):
    """
    Prüft ob ein Schiff an den angegebenen Positionen platziert werden kann.

    Bedingungen:
    - Alle Zellen müssen innerhalb des 10×10 Felds liegen
    - Keine Zelle darf bereits ein Schiff (SHIP) enthalten
    - Zu anderen Schiffen muss mindestens 1 Zelle Abstand sein (inkl. Diagonale)
    """
    # Rand-Prüfung
    for (r, c) in cells:
        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
            return False

    # Abstandsprüfung inkl. alle 8 Nachbarzellen
    for (r, c) in cells:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if my_grid[nr][nc] == SHIP:
                        return False
    return True


def canvas_to_cell(x, y):
    """Wandelt Canvas-Pixel-Koordinaten in Zeile/Spalte um."""
    col = (x - CELL_SIZE) // CELL_SIZE
    row = (y - CELL_SIZE) // CELL_SIZE
    return row, col


def place_ship(row, col):
    """Platziert das nächste ausstehende Schiff an der angegebenen Position."""
    global pending_ships

    if not pending_ships:
        return

    size = pending_ships[0]
    cells = get_ship_cells(row, col, size, placing_h)

    if not is_valid_placement(cells):
        update_status("❌ Ungültige Position! Schiffe müssen Abstand zueinander halten.")
        return

    # Schiff in das Spielfeld eintragen
    for (r, c) in cells:
        my_grid[r][c] = SHIP
    my_ships.append(list(cells))
    pending_ships.pop(0)

    # Sofort nach Änderung neu zeichnen (kein root.after nötig: wir sind im Hauptthread)
    draw_grid(my_canvas, my_grid, show_ships=True)
    update_fleet_label()

    if not pending_ships:
        btn_ready.config(state=tk.NORMAL)
        update_status("✅ Alle Schiffe gesetzt! Klicke 'Fertig' wenn du bereit bist.")
    else:
        direction = "→ Horizontal" if placing_h else "↓ Vertikal"
        update_status(f"Nächstes Schiff: Länge {pending_ships[0]}  |  Ausrichtung: {direction}")


def on_my_canvas_click(event):
    """Klick auf das eigene Spielfeld – Schiff platzieren."""
    if game_phase != "PLACING":
        return
    row, col = canvas_to_cell(event.x, event.y)
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        place_ship(row, col)


def on_my_canvas_motion(event):
    """Mausbewegung über dem eigenen Feld – zeigt Vorschau des nächsten Schiffs."""
    if game_phase != "PLACING" or not pending_ships:
        return

    row, col = canvas_to_cell(event.x, event.y)
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return

    # Normales Spielfeld zeichnen und danach die Vorschau drüberlegen
    draw_grid(my_canvas, my_grid, show_ships=True)

    size = pending_ships[0]
    cells = get_ship_cells(row, col, size, placing_h)
    valid = is_valid_placement(cells)
    color = COLORS["preview"] if valid else COLORS["invalid"]

    for (r, c) in cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            x1 = c * CELL_SIZE + CELL_SIZE
            y1 = r * CELL_SIZE + CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            my_canvas.create_rectangle(x1, y1, x2, y2,
                                       fill=color,
                                       outline=COLORS["grid"])


def toggle_direction():
    """Wechselt zwischen horizontaler und vertikaler Schiffsausrichtung."""
    global placing_h
    placing_h = not placing_h
    text = "→ Horizontal" if placing_h else "↓ Vertikal"
    btn_direction.config(text=f"Ausrichtung: {text}")


# ============================================================================
# SPIELPHASE – GUI-AKTIONEN (VORGEGEBEN – nicht verändern!)
# ============================================================================

def on_enemy_canvas_click(event):
    """Klick auf das Gegnerfeld – Schuss abfeuern (nur wenn ich dran bin)."""
    if not is_my_turn or game_phase != "MY_TURN":
        return

    row, col = canvas_to_cell(event.x, event.y)
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return

    if enemy_grid[row][col] != EMPTY:
        update_status("⚠️  Dieses Feld wurde bereits beschossen!")
        return

    on_shoot(row, col)


# ============================================================================
# SPIELSTEUERUNG – HILFSFUNKTIONEN (VORGEGEBEN – nicht verändern!)
# ============================================================================

def check_both_ready():
    """Startet das Spiel sobald beide Spieler bereit sind."""
    if i_am_ready and opponent_ready:
        root.after(0, start_game)


def start_game():
    """Startet die eigentliche Spielphase (beide haben 'Fertig' gedrückt)."""
    global game_phase, is_my_turn

    # Server fängt an, Client wartet
    is_my_turn = (my_role == "server")
    game_phase = "MY_TURN" if is_my_turn else "OPPONENT_TURN"

    # Platzierungs-Steuerelemente ausblenden
    btn_direction.grid_remove()
    fleet_label.grid_remove()
    btn_ready.config(text="▶ Spiel läuft", state=tk.DISABLED)

    draw_my_grid()
    draw_enemy_grid()

    if is_my_turn:
        update_status("🎯 Du fängst an! Klicke auf das Gegnerfeld zum Schießen.")
        enemy_canvas.bind("<Button-1>", on_enemy_canvas_click)
    else:
        update_status("⏳ Gegner fängt an. Warte auf den ersten Schuss...")


def switch_to_my_turn():
    """Aktiviert meinen Spielzug."""
    global is_my_turn, game_phase
    is_my_turn = True
    game_phase = "MY_TURN"
    update_status("🎯 Dein Zug! Klicke auf das Gegnerfeld zum Schießen.")
    root.after(0, lambda: enemy_canvas.bind("<Button-1>", on_enemy_canvas_click))


def switch_to_opponent_turn():
    """Wechselt auf den Zug des Gegners."""
    global is_my_turn, game_phase
    is_my_turn = False
    game_phase = "OPPONENT_TURN"
    update_status("⏳ Gegner ist dran. Warte auf seinen Schuss...")
    root.after(0, lambda: enemy_canvas.unbind("<Button-1>"))


def end_game(i_won):
    """
    Beendet das Spiel.

    Parameter:
        i_won (bool): True  → ich habe gewonnen
                      False → ich habe verloren
    """
    global game_phase
    game_phase = "GAME_OVER"
    root.after(0, lambda: enemy_canvas.unbind("<Button-1>"))

    if i_won:
        root.after(0, lambda: update_status(
            "🏆 Du hast GEWONNEN! Alle Schiffe des Gegners versenkt!"))
        root.after(200, lambda: messagebox.showinfo(
            "Gewonnen! 🏆",
            "Glückwunsch!\nDu hast gewonnen!\n\nAlle Schiffe des Gegners wurden versenkt."))
    else:
        root.after(0, lambda: update_status(
            "💥 Du hast verloren. Alle deine Schiffe wurden versenkt."))
        root.after(200, lambda: messagebox.showinfo(
            "Verloren 💥",
            "Leider verloren!\nAlle deine Schiffe wurden versenkt.\n\nViel Glück beim nächsten Mal!"))


def mark_my_hit(row, col):
    """Markiert einen Treffer auf dem eigenen Feld und aktualisiert die Anzeige."""
    my_grid[row][col] = HIT
    draw_my_grid()


def mark_my_miss(row, col):
    """Markiert einen Fehlschuss auf dem eigenen Feld und aktualisiert die Anzeige."""
    my_grid[row][col] = MISS
    draw_my_grid()


def mark_enemy_hit(row, col):
    """Markiert einen Treffer auf dem Gegnerfeld und aktualisiert die Anzeige."""
    enemy_grid[row][col] = HIT
    draw_enemy_grid()


def mark_enemy_miss(row, col):
    """Markiert einen Fehlschuss auf dem Gegnerfeld und aktualisiert die Anzeige."""
    enemy_grid[row][col] = MISS
    draw_enemy_grid()


# ============================================================================
# ████████████████████████████████████████████████████████████████████████████
# ❗❗❗                 EUER BEREICH – AUFGABEN 1 – 8                  ❗❗❗
# ████████████████████████████████████████████████████████████████████████████
# ============================================================================


# ----------------------------------------------------------------------------
# ❗ AUFGABE 1: PROTOKOLL-KONSTANTEN
# ----------------------------------------------------------------------------
# Definiert eure Protokoll-Nachrichten als Konstanten.
# Beide Spieler (Server und Client) MÜSSEN dieselben Nachrichten verwenden!
#
# Überlegt gemeinsam:
#   Welche Ereignisse müssen übertragen werden?
#   Wie viele Informationen braucht jede Nachricht?
#
# Beispiel-Vorschlag (ihr könnt andere Namen und Formate wählen!):
#
#   MSG_READY  = "FERTIG"          # Spieler ist bereit (Schiffe gesetzt)
#   MSG_SHOOT  = "SCHUSS"          # Schuss abgefeuert
#   MSG_HIT    = "TREFFER"         # Schuss hat getroffen
#   MSG_MISS   = "WASSER"          # Schuss hat daneben getroffen
#   MSG_SUNK   = "VERSENKT"        # Ein Schiff wurde vollständig versenkt
#   MSG_WIN    = "VERLOREN"        # Alle meine Schiffe versenkt (ich habe verloren)
#
# Nachrichten-Format (Beispiel):
#   "FERTIG"           → kein Parameter nötig
#   "SCHUSS:3,5"       → Zeile 3, Spalte 5 (getrennt durch ":")
#   "TREFFER:3,5"      → Zeile 3, Spalte 5 wurde getroffen
#   "WASSER:3,5"       → Zeile 3, Spalte 5 war Wasser
#   "VERSENKT:3,5,3,H" → Schiff an (3,5), Länge 3, Richtung Horizontal (optional)
#   "VERLOREN"         → ich habe verloren, Gegner hat gewonnen
# ----------------------------------------------------------------------------

# Fügt eure Protokoll-Konstanten hier ein:
# MSG_READY = ???
# MSG_SHOOT = ???
# MSG_HIT   = ???
# MSG_MISS  = ???
# MSG_SUNK  = ???
# MSG_WIN   = ???


# ----------------------------------------------------------------------------
# ❗ AUFGABE 2: NACHRICHT SENDEN
# ----------------------------------------------------------------------------
# Implementiert send_message() so dass eine Zeichenkette über das Netzwerk
# an den Gegner gesendet wird.
#
# Wichtige Hinweise:
#   - "conn" ist die globale Variable mit der aktiven Netzwerkverbindung
#   - Texte müssen mit .encode() in Bytes umgewandelt werden
#     (Netzwerke übertragen nur Bytes, keine Strings direkt)
#   - Hängt '\n' ans Ende der Nachricht → der Empfänger erkennt damit
#     wo eine Nachricht aufhört und die nächste beginnt
#   - sendall() stellt sicher dass ALLE Bytes wirklich gesendet werden
#   - Wickelt den Sendvorgang in try/except → falls die Verbindung bricht,
#     stürzt das Programm nicht ab
# ----------------------------------------------------------------------------

def send_message(msg):
    """
    Sendet eine Protokoll-Nachricht an den Gegner.

    Parameter:
        msg (str): Die Nachricht, z.B. "FERTIG" oder "SCHUSS:3,5"

    Hinweis:
        Hängt automatisch '\n' ans Ende damit der Empfänger die
        Nachrichtengrenze erkennt.

    Beispiele:
        send_message("FERTIG")      → sendet "FERTIG\\n" über das Netzwerk
        send_message("SCHUSS:3,5") → sendet "SCHUSS:3,5\\n"
    """
    global conn

    # ❗ TODO: Implementiert diese Funktion!
    #
    # Tipp:
    #   try:
    #       conn.sendall((msg + "\n").encode())
    #       print(f"[GESENDET] {msg}")
    #   except Exception as e:
    #       print(f"[FEHLER beim Senden] {e}")

    pass  # Diese Zeile entfernen wenn ihr die Funktion implementiert habt


# ----------------------------------------------------------------------------
# ❗ AUFGABE 3: NACHRICHTEN EMPFANGEN UND VERARBEITEN
# ----------------------------------------------------------------------------
# handle_message() wird AUTOMATISCH aufgerufen, wenn eine Nachricht vom Gegner
# ankommt (der Empfangs-Thread kümmert sich darum).
#
# Eure Aufgabe:
#   1. Nachricht analysieren (welcher Befehl steckt drin?)
#   2. Parameter auslesen (z.B. Zeile und Spalte)
#   3. Richtige Hilfsfunktionen aufrufen
#
# Bereitgestellte Hilfsfunktionen die ihr aufrufen könnt:
#   mark_enemy_hit(row, col)    → zeigt Treffer auf Gegnerfeld an
#   mark_enemy_miss(row, col)   → zeigt Verfehlt auf Gegnerfeld an
#   mark_my_hit(row, col)       → zeigt Treffer auf eigenem Feld an
#   mark_my_miss(row, col)      → zeigt Verfehlt auf eigenem Feld an
#   switch_to_my_turn()         → aktiviert meinen Zug (gibt Klicks frei)
#   switch_to_opponent_turn()   → Gegner ist wieder dran
#   check_both_ready()          → prüft ob Spiel starten kann
#   end_game(i_won=True/False)  → zeigt Gewinn/Verlust-Nachricht
#   update_status("Text...")    → aktualisiert die Statuszeile oben
#   process_shot(row, col)      → verarbeitet Schuss des Gegners auf unser Feld
#
# Nachrichten aufteilen:
#   msg = "SCHUSS:3,5"
#   teile = msg.split(":")      → ["SCHUSS", "3,5"]
#   befehl = teile[0]           → "SCHUSS"
#   row, col = map(int, teile[1].split(","))  → row=3, col=5
# ----------------------------------------------------------------------------

def handle_message(msg):
    """
    Verarbeitet eine empfangene Nachricht vom Gegner.

    Parameter:
        msg (str): Die Nachricht ohne '\\n', z.B. "SCHUSS:3,5"

    Diese Funktion wird automatisch vom Empfangs-Thread aufgerufen.
    Alle GUI-Updates sind thread-sicher (über root.after in den Hilfsfunktionen).
    """
    global opponent_ready

    print(f"[EMPFANGEN] {msg}")   # Debug: Zeigt alle eingehenden Nachrichten

    # ❗ TODO: Implementiert die Nachrichtenverarbeitung!
    #
    # Beispielstruktur (mit euren eigenen Konstanten!):
    #
    #   teile   = msg.split(":")
    #   befehl  = teile[0]
    #
    #   if befehl == MSG_READY:
    #       opponent_ready = True
    #       check_both_ready()
    #
    #   elif befehl == MSG_SHOOT:
    #       row, col = map(int, teile[1].split(","))
    #       process_shot(row, col)
    #
    #   elif befehl == MSG_HIT:
    #       row, col = map(int, teile[1].split(","))
    #       mark_enemy_hit(row, col)
    #       switch_to_my_turn()         # oder: nochmal schießen nach Treffer?
    #
    #   elif befehl == MSG_MISS:
    #       row, col = map(int, teile[1].split(","))
    #       mark_enemy_miss(row, col)
    #       switch_to_opponent_turn()   # Gegner ist wieder dran
    #
    #   elif befehl == MSG_SUNK:
    #       update_status("💥 Eines deiner Schiffe wurde versenkt!")
    #
    #   elif befehl == MSG_WIN:
    #       end_game(i_won=True)        # Gegner meldet Verlust → ich habe gewonnen

    pass  # Diese Zeile entfernen wenn ihr die Funktion implementiert habt


# ----------------------------------------------------------------------------
# ❗ AUFGABE 4: SCHUSS DES GEGNERS VERARBEITEN
# ----------------------------------------------------------------------------
# Wenn der Gegner auf unser Feld schießt (wir MSG_SHOOT empfangen),
# muss process_shot() entscheiden was passiert.
#
# Ablauf:
#   1. Prüfe ob my_grid[row][col] == SHIP
#
#   2a. TREFFER (cell == SHIP):
#       a) mark_my_hit(row, col) aufrufen
#       b) Herausfinden welches Schiff diese Zelle enthält
#          (suche in my_ships nach einem Ship das (row,col) enthält)
#       c) check_sunk(schiff) aufrufen für dieses Schiff
#       d) Wenn versenkt: eine VERSENKT-Nachricht senden (optional)
#       e) check_all_sunk() aufrufen
#       f) Wenn alle versenkt:
#              send_message(MSG_WIN) und end_game(i_won=False)
#          Sonst:
#              send_message(TREFFER-Nachricht)
#       g) Überlegt: Dar der Gegner nach einem Treffer nochmals schießen?
#          Falls ja: switch_to_opponent_turn() (Gegner bleibt dran)
#          Falls nein: switch_to_my_turn() (ich bin dran)
#
#   2b. VERFEHLT (cell != SHIP):
#       a) mark_my_miss(row, col)
#       b) send_message(WASSER-Nachricht mit row und col)
#       c) switch_to_my_turn() → ich bin jetzt wieder dran
# ----------------------------------------------------------------------------

def process_shot(row, col):
    """
    Verarbeitet einen Schuss des Gegners auf unser Spielfeld.

    Parameter:
        row (int): Zeile des Schusses (0–9)
        col (int): Spalte des Schusses (0–9)
    """

    # ❗ TODO: Implementiert diese Funktion!

    pass  # Diese Zeile entfernen wenn ihr die Funktion implementiert habt


# ----------------------------------------------------------------------------
# ❗ AUFGABE 5: SCHIFF VERSENKT PRÜFEN
# ----------------------------------------------------------------------------

def check_sunk(ship_cells):
    """
    Prüft ob ein Schiff vollständig versenkt wurde (alle Zellen getroffen).

    Parameter:
        ship_cells (list): Liste von (row, col) Tupeln des Schiffs,
                           z.B. [(0,0), (0,1), (0,2)] für ein 3er-Schiff

    Rückgabe:
        True  → alle Zellen des Schiffs wurden getroffen (HIT)
        False → mindestens eine Zelle hat noch keinen Treffer

    Tipp:
        Prüft für jede Position (r, c) in ship_cells ob my_grid[r][c] == HIT.
        all([...]) gibt True zurück wenn ALLE Elemente True sind.
        Beispiel: all(my_grid[r][c] == HIT for (r, c) in ship_cells)
    """

    # ❗ TODO: Implementiert diese Funktion!
    return False   # ← Platzhalter! Ändert das!


# ----------------------------------------------------------------------------
# ❗ AUFGABE 6: ALLE SCHIFFE VERSENKT PRÜFEN
# ----------------------------------------------------------------------------

def check_all_sunk():
    """
    Prüft ob alle eigenen Schiffe vollständig versenkt wurden.

    Rückgabe:
        True  → alle Schiffe sind vollständig versenkt
        False → mindestens ein Schiff ist noch nicht versenkt

    Tipp:
        Ruft check_sunk() für jedes Schiff in my_ships auf.
        all([check_sunk(schiff) for schiff in my_ships])
    """

    # ❗ TODO: Implementiert diese Funktion!
    return False   # ← Platzhalter! Ändert das!


# ----------------------------------------------------------------------------
# ❗ AUFGABE 7: on_shoot() – Schuss abschicken
# ----------------------------------------------------------------------------
# Diese Funktion wird aufgerufen wenn der Spieler auf das Gegnerfeld klickt.
# Die meiste Logik ist bereits vorgegeben.
# Eure Aufgabe: Die richtige send_message()-Zeile einfügen!
# ----------------------------------------------------------------------------

def on_shoot(row, col):
    """
    Wird aufgerufen wenn der Spieler auf ein Feld des Gegners klickt.

    Parameter:
        row, col (int): Position des Schusses (0–9)

    Diese Funktion:
    - Deaktiviert das Gegnerfeld (kein weiteres Klicken bis Antwort kommt)
    - Sendet den Schuss über das Netzwerk
    - Wartet auf die Antwort (TREFFER oder WASSER) des Gegners
    """
    global is_my_turn, game_phase

    # Klicks deaktivieren bis Antwort kommt
    is_my_turn = False
    game_phase = "WAITING_FOR_RESULT"
    enemy_canvas.unbind("<Button-1>")
    update_status(f"💣 Schuss auf {chr(65 + col)}{row + 1} abgefeuert! Warte auf Ergebnis...")

    # ❗ TODO AUFGABE 7: Sendet hier den Schuss an den Gegner!
    #
    # Nutzt send_message() mit eurer Schuss-Nachricht.
    # Der Gegner muss wissen auf welche Zeile und Spalte ihr geschossen habt.
    #
    # Beispiel:
    #   send_message(f"{MSG_SHOOT}:{row},{col}")
    #
    # Ersetzt die folgende Zeile durch euren Code:
    pass


# ----------------------------------------------------------------------------
# ❗ AUFGABE 8: on_ready_click() – Bereit melden
# ----------------------------------------------------------------------------

def on_ready_click():
    """
    Wird aufgerufen wenn der Spieler auf 'Fertig' klickt.
    Alle Schiffe sind gesetzt – Spieler ist bereit zum Spielen.
    """
    global i_am_ready, game_phase

    if pending_ships:
        messagebox.showwarning("Noch nicht fertig",
                               "Platziere erst alle Schiffe bevor du auf 'Fertig' klickst!")
        return

    i_am_ready = True
    btn_ready.config(state=tk.DISABLED, text="✅ Bereit!")
    game_phase = "WAITING"
    update_status("✅ Du bist bereit! Warte auf den Gegner...")

    # ❗ TODO AUFGABE 8: Sendet hier die Bereit-Nachricht an den Gegner!
    #
    # Der Gegner muss wissen dass ihr fertig seid.
    # Nutzt send_message() mit eurer Bereit-Konstante.
    #
    # Beispiel:
    #   send_message(MSG_READY)
    #
    # Ersetzt die folgende Zeile durch euren Code:
    pass

    # Prüfen ob beide bereit sind → Spiel kann starten
    check_both_ready()


# ============================================================================
# ████████████████████████████████████████████████████████████████████████████
# ❗❗❗               ENDE DES AUFGABEN-BEREICHS                       ❗❗❗
# ████████████████████████████████████████████████████████████████████████████
# ============================================================================


# ============================================================================
# NETZWERK – EMPFANGS-SCHLEIFE (VORGEGEBEN – nicht verändern!)
# ============================================================================

def receive_loop():
    """
    Empfangs-Thread: Läuft dauerhaft im Hintergrund und wartet auf Nachrichten.

    Für jede empfangene Zeile wird handle_message() aufgerufen.
    Durch '\n' am Ende jeder gesendeten Nachricht kann der Empfänger
    sicher Nachrichtengrenzen erkennen (Zeilenweise lesen).

    Endet automatisch wenn die Verbindung unterbrochen wird oder
    das Hauptprogramm beendet wird (daemon=True im Thread).
    """
    global conn

    try:
        # makefile() gibt ein dateiähnliches Objekt zurück → erlaubt zeilenweises Lesen
        conn_file = conn.makefile("r", encoding="utf-8")
        for line in conn_file:
            msg = line.strip()
            if msg:
                handle_message(msg)
    except Exception as e:
        if game_phase != "GAME_OVER":
            print(f"[NETZWERK] Verbindung unterbrochen: {e}")
            root.after(0, lambda: messagebox.showerror(
                "Verbindungsfehler",
                "Die Verbindung zum Gegner wurde unterbrochen.\n"
                "Das Spiel kann nicht fortgesetzt werden."))


def accept_client():
    """
    Wird NUR im Server-Modus in einem Hintergrundthread ausgeführt.
    Wartet auf die eingehende Verbindung des Clients.
    """
    global conn

    try:
        conn, addr = sock.accept()
        print(f"[SERVER] Verbunden mit {addr[0]}")
        root.after(0, lambda ip=addr[0]: update_status(
            f"✅ Verbunden mit {ip}! Platziere deine Schiffe."))

        threading.Thread(target=receive_loop, daemon=True).start()

    except Exception as e:
        root.after(0, lambda: messagebox.showerror(
            "Verbindungsfehler", f"Fehler beim Warten auf Verbindung:\n{e}"))


# ============================================================================
# GUI ERSTELLEN (VORGEGEBEN – nicht verändern!)
# ============================================================================

def create_gui():
    """Erstellt das komplette Fenster mit allen Steuerelementen."""
    global status_label, my_canvas, enemy_canvas
    global btn_direction, btn_ready, fleet_label

    canvas_px = GRID_SIZE * CELL_SIZE + CELL_SIZE   # 440 × 440 Pixel

    root.configure(bg="#ECF0F1")

    # ---- Statuszeile (oben) ----
    status_frame = tk.Frame(root, bg="#1A5276", pady=6)
    status_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

    status_label = tk.Label(
        status_frame,
        text="Verbinde...",
        font=("Arial", 12, "bold"),
        bg="#1A5276", fg="white",
        padx=10
    )
    status_label.pack()

    # ---- Spielfeld-Bereich (Mitte) ----
    fields_frame = tk.Frame(root, bg="#ECF0F1", padx=10, pady=10)
    fields_frame.grid(row=1, column=0, columnspan=2)

    # Linkes Feld: Eigenes Spielfeld
    my_frame = tk.LabelFrame(
        fields_frame,
        text="🚢  Mein Feld",
        font=("Arial", 11, "bold"),
        bg="#ECF0F1", padx=5, pady=5
    )
    my_frame.grid(row=0, column=0, padx=15)

    my_canvas = tk.Canvas(
        my_frame,
        width=canvas_px, height=canvas_px,
        bg=COLORS["water"],
        highlightthickness=0
    )
    my_canvas.pack()
    my_canvas.bind("<Button-1>", on_my_canvas_click)
    my_canvas.bind("<Motion>", on_my_canvas_motion)

    # Rechtes Feld: Gegnerisches Spielfeld
    enemy_frame = tk.LabelFrame(
        fields_frame,
        text="🎯  Gegnerfeld",
        font=("Arial", 11, "bold"),
        bg="#ECF0F1", padx=5, pady=5
    )
    enemy_frame.grid(row=0, column=1, padx=15)

    enemy_canvas = tk.Canvas(
        enemy_frame,
        width=canvas_px, height=canvas_px,
        bg=COLORS["water"],
        cursor="crosshair",
        highlightthickness=0
    )
    enemy_canvas.pack()

    # Initiale Felder zeichnen
    draw_grid(my_canvas, my_grid, show_ships=True)
    draw_grid(enemy_canvas, enemy_grid, show_ships=False)

    # ---- Steuerungsbereich (unten) ----
    control_frame = tk.Frame(root, bg="#ECF0F1", padx=15, pady=10)
    control_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    btn_direction = tk.Button(
        control_frame,
        text="Ausrichtung: → Horizontal",
        command=toggle_direction,
        font=("Arial", 10),
        bg="#2980B9", fg="white",
        padx=12, pady=6,
        relief=tk.FLAT
    )
    btn_direction.grid(row=0, column=0, padx=8)

    btn_ready = tk.Button(
        control_frame,
        text="✅  Fertig!",
        command=on_ready_click,
        font=("Arial", 10, "bold"),
        bg="#27AE60", fg="white",
        padx=12, pady=6,
        relief=tk.FLAT,
        state=tk.DISABLED
    )
    btn_ready.grid(row=0, column=1, padx=8)

    fleet_label = tk.Label(
        control_frame,
        text="",
        font=("Courier", 10),
        bg="#ECF0F1",
        justify=tk.LEFT,
        padx=10
    )
    fleet_label.grid(row=0, column=2, padx=10, sticky="w")

    update_fleet_label()


# ============================================================================
# INITIALISIERUNG (VORGEGEBEN – nicht verändern!)
# ============================================================================

def init_game(is_server, host=None):
    """
    Wird einmal beim Programmstart aufgerufen.
    Richtet Spielvariablen, GUI und Netzwerkverbindung ein.

    Parameter:
        is_server (bool): True  → Server-Modus (warte auf Verbindung)
                          False → Client-Modus (verbinde mit Server)
        host (str):       IP-Adresse des Servers (nur im Client-Modus nötig)
    """
    global sock, conn, my_role, pending_ships

    my_role = "server" if is_server else "client"

    # Flotte vorbereiten: aus FLEET die Liste aller Schiffsgrößen erstellen
    # Aus [(1,4),(2,3),(3,2),(4,1)] wird [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    for count, size in FLEET:
        pending_ships.extend([size] * count)

    # GUI aufbauen
    root.title("🚢  Schiffe Versenken – Netzwerkspiel")
    create_gui()

    # Netzwerk-Socket erstellen
    # AF_INET  = IPv4-Adressen
    # SOCK_STREAM = TCP (zuverlässige, verbindungsorientierte Übertragung)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if is_server:
        # SERVER: An Port binden und auf Client warten
        sock.bind(("", PORT))
        sock.listen(1)
        update_status(f"🔌 Warte auf Verbindung (Port {PORT})…")
        threading.Thread(target=accept_client, daemon=True).start()

    else:
        # CLIENT: Verbindung zum Server aufbauen
        update_status(f"🔌 Verbinde mit {host}…")
        try:
            sock.connect((host, PORT))
            conn = sock
            update_status("✅ Verbunden! Platziere deine Schiffe.")
            threading.Thread(target=receive_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror(
                "Verbindungsfehler",
                f"Konnte nicht mit {host} verbinden:\n\n{e}\n\n"
                "Läuft der Server bereits?\n"
                "Stimmt die IP-Adresse?")
            sys.exit(1)

    # Status und erstes Schiff
    direction = "→ Horizontal" if placing_h else "↓ Vertikal"
    if pending_ships:
        if not is_server:
            update_status(
                f"✅ Verbunden! Erstes Schiff: Länge {pending_ships[0]}  |  {direction}")
        # (Server-Status wird in accept_client gesetzt)


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

if __name__ == "__main__":
    """
    Einstiegspunkt – wird beim Starten des Skripts ausgeführt.

    Ablauf:
        1. Hauptfenster erstellen (zunächst versteckt)
        2. Spielmodus abfragen (Server oder Client?)
        3. Falls Client: IP-Adresse des Servers abfragen
        4. Spiel initialisieren (Verbindung + GUI aufbauen)
        5. GUI-Hauptschleife starten (hält das Fenster offen)
    """

    root = tk.Tk()
    root.resizable(False, False)
    root.withdraw()   # Fenster erst verstecken bis Modus gewählt ist

    # Spielmodus abfragen
    mode = simpledialog.askstring(
        "Spielmodus wählen",
        "Wie möchtest du spielen?\n\n"
        "  'Server' → Du wartest auf den anderen Spieler\n"
        "  'Client' → Du verbindest dich mit dem anderen Spieler\n\n"
        "Eingabe (Server / Client):"
    )

    if not mode:
        sys.exit(0)

    mode = mode.strip().lower()

    if mode == "server":
        root.deiconify()
        init_game(is_server=True)

    elif mode == "client":
        host = simpledialog.askstring(
            "Server-IP eingeben",
            "IP-Adresse des Server-Computers:\n"
            "(Beispiel: 192.168.1.42)\n\n"
            "Tipp: Der Server-Spieler findet seine IP mit 'ipconfig' в der Eingabeaufforderung."
        )
        if not host:
            sys.exit(0)
        root.deiconify()
        init_game(is_server=False, host=host.strip())

    else:
        messagebox.showerror(
            "Ungültige Eingabe",
            "Bitte nur 'Server' oder 'Client' eingeben.")
        sys.exit(1)

    # GUI-Hauptschleife starten
    # mainloop() wartet auf Benutzer-Events (Klicks, Tasten, …) und
    # läuft bis das Fenster geschlossen wird.
    root.mainloop()


# ============================================================================
# HINWEISE UND ERKLÄRUNGEN
# ============================================================================
"""
THREADING – Warum brauchen wir das?
    Das Programm muss gleichzeitig:
    - Die GUI bedienen (auf Klicks reagieren)
    - Auf eingehende Netzwerknachrichten warten (conn.recv() blockiert!)
    Lösung: receive_loop läuft in einem eigenen Thread im Hintergrund.
    daemon=True → Thread endet automatisch wenn das Hauptprogramm endet.

THREAD-SICHERHEIT – Warum root.after()?
    tkinter-GUI darf NUR aus dem Hauptthread heraus verändert werden.
    Deshalb nutzen die Hilfsfunktionen root.after(0, callback):
    Das "stellt die Aufgabe in die Warteschlange" des Hauptthreads.

SOCKETS – Wie funktioniert die Kommunikation?
    Server:  sock.bind() → sock.listen() → sock.accept() → conn
    Client:  sock.connect() → conn = sock
    Danach:  conn.sendall() zum Senden, conn.makefile() zum Empfangen

PROTOKOLL – Warum '\n' am Ende?
    TCP ist ein "Strom" (stream) ohne vordefinierte Nachrichtengrenzen.
    Durch '\n' am Ende weiß der Empfänger: "Hier endet eine Nachricht."
    makefile().readline() liest genau bis zum nächsten '\n'.
"""
