"""
Tic-Tac-Toe Netzwerkspiel
=========================
Ein Tic-Tac-Toe Spiel für zwei Spieler über ein lokales Netzwerk.

Wichtige Konzepte:
- Client-Server-Architektur: Ein Spieler ist der Server (wartet), der andere ist Client (verbindet sich)
- Sockets: Ermöglichen die Kommunikation zwischen zwei Computern über das Netzwerk
- Threading: Gleichzeitiges Ausführen mehrerer Aufgaben (z.B. GUI und Netzwerk parallel)
- Tkinter: Python-Bibliothek für grafische Benutzeroberflächen (GUI)
"""

import sys
import socket      # Für die Netzwerkkommunikation (Verbindungen zwischen Computern)
import threading   # Für parallele Ausführung (gleichzeitig auf Nachrichten warten und GUI bedienen)
import tkinter as tk  # Für die grafische Oberfläche
from tkinter import simpledialog, messagebox  # Für Eingabefenster und Meldungen

# ============================================================================
# KONSTANTEN - Werte die sich nicht ändern
# ============================================================================

# HOST: IP-Adresse des Servers. Leer = alle Netzwerkschnittstellen auf diesem Computer
HOST = ""

# PORT: Eine "Tür-Nummer" für die Netzwerkverbindung. Beide Spieler müssen denselben Port verwenden
# Ports 0-1023 sind reserviert, daher verwenden wir 65432
PORT = 65432

# ============================================================================
# GLOBALE VARIABLEN - Spielzustand
# ============================================================================

# Das Spielfeld: 3x3 Matrix, am Anfang alle Felder leer ("-")
# Jede innere Liste ist eine Zeile des Spielfelds
board = [["-","-","-"],["-","-","-"],["-","-","-"]]

# Welcher Spieler ist gerade dran? ("X" oder "O")
current_player = "X"

# ============================================================================
# GLOBALE VARIABLEN - Netzwerk und GUI
# ============================================================================

# root: Das Hauptfenster der GUI
root = None

# my_symbol: Welches Symbol habe ICH? ("X" für Server, "O" für Client)
my_symbol = ""

# is_my_turn: Bin ICH gerade am Zug? (True/False)
is_my_turn = False

# moves: Wie viele Züge wurden insgesamt gemacht? (maximal 9)
moves = 0

# sock: Das Socket-Objekt für die Netzwerkverbindung
sock = None

# conn: Die aktive Verbindung zum anderen Spieler
conn = None

# info_label: Das GUI-Element, das anzeigt wer dran ist
info_label = None

# buttons: 3x3 Matrix mit allen Buttons des Spielfelds
buttons = []

# ============================================================================
# SPIELLOGIK-FUNKTIONEN
# ============================================================================
# Diese Funktionen kennen die Schüler bereits aus der Vorlage!
# Sie kümmern sich um die Spielregeln von Tic-Tac-Toe.

def check_winner(player):
    """
    Prüft ob ein bestimmter Spieler gewonnen hat.
    
    Parameter:
        player: Das zu prüfende Symbol ("X" oder "O")
    
    Rückgabe:
        True wenn der Spieler gewonnen hat, sonst False
    
    Gewinn-Bedingungen:
        1. Drei gleiche Symbole in einer Zeile (horizontal)
        2. Drei gleiche Symbole in einer Spalte (vertikal)
        3. Drei gleiche Symbole diagonal (links-oben nach rechts-unten)
        4. Drei gleiche Symbole diagonal (rechts-oben nach links-unten)
    """
    global board
    
    # Prüfe alle 3 Zeilen und alle 3 Spalten
    for i in range(3):
        # Zeile prüfen: Sind alle 3 Felder in Zeile i gleich dem player?
        # board[i][j] bedeutet: Zeile i, Spalte j
        # all() gibt True zurück wenn ALLE Elemente True sind
        if all(board[i][j] == player for j in range(3)):
            return True  # Gewonnen durch horizontale Linie
        
        # Spalte prüfen: Sind alle 3 Felder in Spalte i gleich dem player?
        if all(board[j][i] == player for j in range(3)):
            return True  # Gewonnen durch vertikale Linie
    
    # Diagonale von links-oben nach rechts-unten prüfen
    # Positionen: (0,0), (1,1), (2,2)
    if all(board[i][i] == player for i in range(3)):
        return True  # Gewonnen durch Hauptdiagonale
    
    # Diagonale von rechts-oben nach links-unten prüfen
    # Positionen: (0,2), (1,1), (2,0)
    # board[i][2-i] ergibt: i=0→(0,2), i=1→(1,1), i=2→(2,0)
    if all(board[i][2 - i] == player for i in range(3)):
        return True  # Gewonnen durch Nebendiagonale
    
    # Keine Gewinn-Bedingung erfüllt
    return False


def make_move(row, col, symbol):
    """
    Führt einen Zug aus und aktualisiert das Spielfeld.
    Diese Funktion wird für BEIDE Spieler verwendet (eigene und gegnerische Züge).
    
    Parameter:
        row: Zeile (0-2)
        col: Spalte (0-2)
        symbol: Das Symbol das gesetzt wird ("X" oder "O")
    
    Ablauf:
    1. Setze Symbol im Spielfeld-Array
    2. Aktualisiere den Button in der GUI
    3. Erhöhe den Zug-Zähler
    4. Prüfe ob jemand gewonnen hat
    5. Prüfe ob das Spiel unentschieden ist
    6. Wenn noch weitergeht: Wechsle den aktuellen Spieler
    """
    global board, current_player, buttons, info_label, moves
    
    # 1. Setze das Symbol im internen Spielfeld (im Speicher)
    board[row][col] = symbol
    
    # 2. Aktualisiere den entsprechenden Button in der GUI
    buttons[row][col].config(text=symbol)
    
    # 3. Erhöhe den Zähler für gemachte Züge
    moves += 1
    
    # 4. Prüfe ob das aktuelle Symbol gewonnen hat
    if check_winner(symbol):
        info_label.config(text=f"Spieler {symbol} gewinnt!")
        disable_all_buttons()  # Spiel ist vorbei, keine Züge mehr möglich
    
    # 5. Prüfe ob alle 9 Felder belegt sind (Unentschieden)
    elif moves == 9:
        info_label.config(text="Unentschieden!")
        disable_all_buttons()
    
    # 6. Spiel geht weiter: Wechsle den Spieler
    else:
        # Wenn aktuell "X" dran ist → wechsle zu "O", sonst zu "X"
        current_player = "O" if current_player == "X" else "X"
        info_label.config(text=f"Aktueller Spieler: {current_player}")


# ============================================================================
# GUI-FUNKTIONEN (Graphical User Interface)
# ============================================================================
# Diese Funktionen verwalten die grafische Oberfläche (Buttons, Labels, etc.)

def disable_all_buttons():
    """
    Deaktiviert alle Spielfeld-Buttons.
    Wird aufgerufen wenn das Spiel vorbei ist (Gewinn oder Unentschieden).
    
    Deaktivierte Buttons können nicht mehr angeklickt werden.
    """
    global buttons
    
    # Durchlaufe alle Zeilen
    for row in buttons:
        # Durchlaufe alle Buttons in der Zeile
        for btn in row:
            # state=tk.DISABLED macht den Button grau und nicht anklickbar
            btn.config(state=tk.DISABLED)


def update_buttons():
    """
    Aktualisiert den Zustand aller Buttons (aktiviert oder deaktiviert).
    
    Ein Button ist NUR anklickbar wenn:
        1. ICH bin am Zug (is_my_turn == True)
        2. UND das Feld ist noch leer (board[r][c] == "-")
    
    Diese Funktion wird aufgerufen:
        - Nach jedem eigenen Zug (um eigene Buttons zu deaktivieren)
        - Nach jedem gegnerischen Zug (um eigene Buttons zu aktivieren)
    """
    global board, buttons, is_my_turn
    
    # Durchlaufe alle Zeilen (0, 1, 2)
    for r in range(3):
        # Durchlaufe alle Spalten (0, 1, 2)
        for c in range(3):
            # Prüfe beide Bedingungen
            if is_my_turn and board[r][c] == "-":
                # Button aktivieren (kann angeklickt werden)
                buttons[r][c].config(state=tk.NORMAL)
            else:
                # Button deaktivieren (kann NICHT angeklickt werden)
                buttons[r][c].config(state=tk.DISABLED)


# ============================================================================
# BENUTZER-INTERAKTION
# ============================================================================
# Diese Funktion verbindet die GUI mit der Spiellogik und dem Netzwerk

def handle_click(row, col):
    """
    Wird aufgerufen wenn ein Spieler auf einen Button klickt.
    
    Parameter:
        row: Zeile des angeklickten Feldes (0, 1 oder 2)
        col: Spalte des angeklickten Feldes (0, 1 oder 2)
    
    Ablauf:
    1. Prüfe ob der Spieler überhaupt dran ist
    2. Prüfe ob das Feld noch frei ist
    3. Führe den Zug aus (setze Symbol)
    4. Sende den Zug an den Gegner über das Netzwerk
    5. Deaktiviere eigene Buttons (Gegner ist jetzt dran)
    """
    global board, is_my_turn, my_symbol
    
    # Überprüfungen BEVOR der Zug ausgeführt wird:
    # - Bin ich überhaupt dran? (is_my_turn muss True sein)
    # - Ist das Feld noch frei? (board[row][col] muss "-" sein)
    if not is_my_turn or board[row][col] != "-":
        return  # Abbruch: Zug ist nicht erlaubt
    
    # Zug ist erlaubt, führe ihn aus
    make_move(row, col, my_symbol)
    
    # Sende meinen Zug an den anderen Spieler über das Netzwerk
    send_move(row, col)
    
    # Jetzt ist der Gegner dran
    is_my_turn = False
    
    # Aktualisiere die Buttons (eigene werden deaktiviert)
    update_buttons()


# ============================================================================
# NETZWERK-FUNKTIONEN
# ============================================================================
# Diese Funktionen ermöglichen die Kommunikation zwischen zwei Computern.
# NEU: Sockets und Threading - fortgeschrittene Konzepte!

def send_move(row, col):
    """
    Sendet den eigenen Zug an den Gegner über das Netzwerk.
    
    Parameter:
        row: Zeile des Zuges
        col: Spalte des Zuges
    
    Datenformat:
        Der Zug wird als String "row,col" gesendet (z.B. "1,2" für Zeile 1, Spalte 2)
        und mit encode() in Bytes umgewandelt (Netzwerke übertragen nur Bytes)
    """
    global conn
    
    try:
        # Format: "Zeile,Spalte" als String
        message = f"{row},{col}"
        
        # Debug-Ausgabe (hilft beim Testen/Fehlersuche)
        print(f"Sende Zug: {message}")
        
        # encode() wandelt String in Bytes um (Netzwerke verstehen nur Bytes)
        # sendall() stellt sicher dass ALLE Bytes gesendet werden
        conn.sendall(message.encode())
    
    except Exception:
        # Falls ein Fehler auftritt (z.B. Verbindung unterbrochen),
        # ignorieren wir ihn einfach (pass = tue nichts)
        pass


def receive_move():
    """
    Wartet auf eingehende Züge vom Gegner.
    Diese Funktion läuft in einem eigenen Thread (parallel zur GUI).
    
    Endlos-Schleife:
        Die Funktion läuft immer weiter und wartet auf neue Daten.
        Sie endet nur wenn:
        - Die Verbindung unterbrochen wird
        - Ein Fehler auftritt
        - Das Hauptprogramm beendet wird (weil daemon=True)
    
    Ablauf:
    1. Warte auf Daten vom Gegner (conn.recv blockiert)
    2. Wenn Daten ankommen, decodiere sie
    3. Extrahiere Zeile und Spalte
    4. Führe den Zug des Gegners aus
    5. Jetzt bin ICH wieder dran
    """
    global conn, my_symbol, is_my_turn
    
    # Endlos-Schleife: Warte immer auf neue Züge
    while True:
        try:
            # recv(1024) wartet auf Daten und empfängt maximal 1024 Bytes
            # Diese Zeile "blockiert" (wartet) bis Daten ankommen
            data = conn.recv(1024)
            
            # Wenn keine Daten mehr kommen, ist die Verbindung unterbrochen
            if not data:
                break  # Beende die Schleife
            
            # decode() wandelt Bytes zurück in String (z.B. "1,2")
            # split(",") trennt den String an jedem Komma (ergibt Liste ["1", "2"])
            # map(int, ...) wandelt beide Strings in Zahlen um
            row, col = map(int, data.decode().split(","))
            
            # Bestimme das Symbol des Gegners
            # Wenn ich "X" bin, ist der Gegner "O" und umgekehrt
            opponent = "O" if my_symbol == "X" else "X"
            
            # Führe den Zug des Gegners aus
            make_move(row, col, opponent)
            
            # Der Gegner hat seinen Zug gemacht, jetzt bin ICH wieder dran
            is_my_turn = True
            
            # Aktiviere meine Buttons wieder
            update_buttons()
        
        except Exception:
            # Bei einem Fehler (z.B. Verbindung unterbrochen) breche ab
            break


def accept_client():
    """
    Diese Funktion wird NUR vom Server ausgeführt.
    Sie wartet auf eine eingehende Verbindung vom Client.
    
    Ablauf:
    1. sock.accept() blockiert (wartet) bis ein Client sich verbindet
    2. Wenn Client verbindet, gibt accept() die Verbindung zurück
    3. Info-Label wird aktualisiert
    4. Ein neuer Thread startet, um Züge des Clients zu empfangen
    """
    global conn, current_player, info_label
    
    # sock.accept() wartet auf eingehende Verbindung und gibt zwei Werte zurück:
    # - conn: Die Verbindung zum Client
    # - _: Die Adresse des Clients (ignorieren wir hier mit "_")
    conn, _ = sock.accept()
    
    # Zeige in der GUI an, dass die Verbindung steht und wer dran ist
    info_label.config(text=f"Aktueller Spieler: {current_player}")
    
    # Starte einen neuen Thread, der im Hintergrund auf Züge wartet
    # daemon=True bedeutet: Thread endet automatisch wenn Hauptprogramm endet
    threading.Thread(target=receive_move, daemon=True).start()



# ============================================================================
# INITIALISIERUNGS-FUNKTION
# ============================================================================

def init_game(is_server, host=None):
    """
    Initialisiert das Spiel - wird einmal am Anfang aufgerufen.
    
    Parameter:
        is_server: True wenn dieser Computer der Server ist, False wenn Client
        host: IP-Adresse des Servers (nur relevant wenn is_server=False)
    
    Diese Funktion:
        1. Setzt alle Spielvariablen
        2. Erstellt die GUI (Fenster, Label, Buttons)
        3. Richtet die Netzwerkverbindung ein
        4. Startet ggf. Threads für Netzwerkkommunikation
    
    Unterschied Server/Client:
        - Server: Wartet auf Verbindung, spielt als "X", Gegner beginnt
        - Client: Verbindet sich aktiv, spielt als "O", beginnt selbst
    """
    global root, my_symbol, is_my_turn, sock, conn, info_label, buttons, current_player
    
    # --- 1. SPIELVARIABLEN SETZEN ---
    
    root.title("Tic-Tac-Toe Netzwerk")
    
    # Server spielt immer "X", Client spielt immer "O"
    my_symbol = "X" if is_server else "O"
    
    # Client beginnt (ist zuerst dran), Server wartet
    # not is_server bedeutet: True wenn Client, False wenn Server
    is_my_turn = not is_server
    
    # Da der Client ("O") immer zuerst spielt, ist der aktuelle Spieler "O"
    current_player = "O"
    
    # Erstelle ein Socket-Objekt
    # AF_INET = IPv4 Adressfamilie (Standard Internet-Adressen)
    # SOCK_STREAM = TCP (zuverlässige, verbindungsorientierte Übertragung)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Noch keine aktive Verbindung
    conn = None

    # --- 2. GUI ERSTELLEN ---
    
    # Label oben: Zeigt an welcher Spieler gerade dran ist
    info_label = tk.Label(root, text=f"Aktueller Spieler: {current_player}")
    info_label.grid(row=0, column=0, columnspan=3)  # Über alle 3 Spalten
    
    # Erstelle 3x3 Matrix mit Buttons
    # List Comprehension: Erstellt verschachtelte Listen in einer Zeile
    buttons = [[tk.Button(root, text="-", width=10, height=3, font=("Arial", 24)) for _ in range(3)] for _ in range(3)]
    
    # Platziere alle Buttons im Grid-Layout
    for r in range(3):
        for c in range(3):
            btn = buttons[r][c]
            
            # Lambda-Funktion mit Default-Argumenten:
            # Ohne row=r, col=c würden alle Buttons die gleichen Werte verwenden (Closure-Problem)
            # Mit Default-Argumenten wird der aktuelle Wert "eingefroren"
            btn.config(command=lambda row=r, col=c: handle_click(row, col))
            
            # Platziere Button im Grid
            # row=r+1 weil Zeile 0 vom info_label belegt ist
            btn.grid(row=r+1, column=c)
    
    # Buttons aktivieren/deaktivieren je nach Spielsituation
    update_buttons()

    # --- 3. NETZWERK EINRICHTEN ---
    
    if is_server:
        # === SERVER-MODUS ===
        
        # Socket an Adresse und Port binden
        # HOST ist "" = alle verfügbaren Netzwerkschnittstellen
        # PORT ist 65432 (unsere gewählte "Tür-Nummer")
        sock.bind((HOST, PORT))
        
        # Lauschen auf eingehende Verbindungen
        # 1 = Maximale Anzahl wartender Verbindungen in der Warteschlange
        sock.listen(1)
        
        # Zeige Wartemeldung
        info_label.config(text="Warte auf Verbindung...")
        
        # Starte einen Thread der auf Client wartet
        # Wichtig: Dies passiert im Hintergrund, damit die GUI nicht "einfriert"
        threading.Thread(target=accept_client, daemon=True).start()
        
    else:
        # === CLIENT-MODUS ===
        
        try:
            # Versuche Verbindung zum Server herzustellen
            # host = die eingegebene IP-Adresse des Servers
            # PORT = 65432 (muss mit Server übereinstimmen)
            sock.connect((host, PORT))
            
            # Verbindung erfolgreich! sock ist jetzt die Verbindung
            conn = sock
            
            # Starte Thread zum Empfangen von Zügen
            threading.Thread(target=receive_move, daemon=True).start()
            
        except Exception as e:
            # Verbindung fehlgeschlagen (Server nicht erreichbar?)
            messagebox.showerror("Fehler", f"Verbindung fehlgeschlagen: {e}")
            sys.exit(1)  # Beende Programm mit Fehlercode


# ============================================================================
# HAUPTPROGRAMM - Wird beim Programmstart ausgeführt
# ============================================================================

if __name__ == "__main__":
    """
    Dieser Code wird nur ausgeführt wenn das Skript direkt gestartet wird
    (nicht wenn es als Modul importiert wird).
    
    Ablauf:
    1. Erstelle Hauptfenster (versteckt)
    2. Frage Benutzer: Server oder Client?
    3. Falls Client: Frage nach Server-IP
    4. Initialisiere das Spiel
    5. Starte GUI-Hauptschleife (wartet auf Benutzer-Interaktionen)
    """
    
    # Erstelle das Hauptfenster
    root = tk.Tk()
    
    # Verstecke das Fenster zunächst (withdraw = zurückziehen)
    # Grund: Wir wollen erst Modus abfragen, bevor das Spielfeld erscheint
    root.withdraw()
    
    # --- MODUS ABFRAGEN ---
    
    # Zeige Eingabefenster für Modus-Wahl
    mode = simpledialog.askstring(
        "Modus wählen",  # Titel des Fensters
        "Server oder Client? (Gib 'Server' oder 'Client' ein):"  # Fragetext
    )
    
    # Wenn Benutzer abbricht (None zurückgegeben wird)
    if not mode:
        sys.exit(0)  # Beende Programm normal (Exitcode 0 = kein Fehler)

    # --- SPIEL STARTEN JE NACH MODUS ---
    
    # Vergleiche Eingabe (in Kleinbuchstaben umgewandelt)
    if mode.lower() == "server":
        # === SERVER WIRD GESTARTET ===
        
        root.deiconify()  # Zeige das Hauptfenster (deiconify = ent-verstecken)
        init_game(is_server=True)  # Initialisiere als Server
        
    elif mode.lower() == "client":
        # === CLIENT WIRD GESTARTET ===
        
        # Frage nach IP-Adresse des Servers
        host = simpledialog.askstring(
            "Server-IP eingeben",
            "Bitte IP-Adresse des Servers eingeben:"
        )
        
        # Wenn keine IP eingegeben wurde, abbrechen
        if not host:
            sys.exit(0)
            
        root.deiconify()  # Zeige das Hauptfenster
        init_game(is_server=False, host=host)  # Initialisiere als Client mit Server-IP
        
    else:
        # === UNGÜLTIGE EINGABE ===
        
        messagebox.showerror("Fehler", "Ungültiger Modus. Bitte 'Server' oder 'Client' eingeben.")
        sys.exit(0)

    # --- STARTE GUI-HAUPTSCHLEIFE ---
    
    # mainloop() ist eine Endlos-Schleife die:
    # - Auf Benutzer-Events wartet (Mausklicks, Tastatur, etc.)
    # - Die GUI aktualisiert
    # - Läuft bis das Fenster geschlossen wird
    root.mainloop()


# ============================================================================
# ZUSÄTZLICHE HINWEISE FÜR SCHÜLER:
# ============================================================================
"""
Wichtige Konzepte die in diesem Programm verwendet werden:

1. CLIENT-SERVER-ARCHITEKTUR:
   - Server: Wartet auf Verbindungen (passiv)
   - Client: Stellt Verbindung her (aktiv)
   - Beide können danach gleichberechtigt Daten senden/empfangen

2. SOCKETS:
   - socket.socket(): Erstellt einen Socket (Endpunkt für Netzwerkkommunikation)
   - bind(): Bindet Socket an Adresse und Port (nur Server)
   - listen(): Lauscht auf eingehende Verbindungen (nur Server)
   - accept(): Akzeptiert eine Verbindung (nur Server, blockiert bis Client verbindet)
   - connect(): Verbindet sich mit Server (nur Client)
   - send()/sendall(): Sendet Daten über die Verbindung
   - recv(): Empfängt Daten (blockiert bis Daten ankommen)

3. THREADING:
   - Ermöglicht parallele Ausführung mehrerer Aufgaben
   - Wichtig hier: GUI muss reaktionsfähig bleiben während auf Netzwerk gewartet wird
   - daemon=True: Thread endet automatisch wenn Hauptprogramm endet

4. TKINTER GUI:
   - tk.Tk(): Hauptfenster
   - tk.Label(): Textanzeige
   - tk.Button(): Anklickbare Schaltfläche
   - grid(): Layout-Manager für tabellarische Anordnung
   - config(): Ändert Eigenschaften eines Widgets
   - mainloop(): Startet Event-Verarbeitung

5. GLOBALE VARIABLEN:
   - Variablen die außerhalb von Funktionen definiert sind
   - Mit 'global' Schlüsselwort in Funktionen änderbar
   - Nützlich für Spielzustand der von vielen Funktionen gebraucht wird

ERWEITERUNGSIDEEN:
- Mehrere Spiele hintereinander (mit Reset-Button)
- Chat-Funktion zwischen Spielern
- Statistik (Anzahl Siege pro Spieler)
- Schönere GUI mit Farben und Bildern
- KI-Gegner als Alternative zum Netzwerk-Modus
- Broadcasting um Server im Netzwerk automatisch zu finden
"""