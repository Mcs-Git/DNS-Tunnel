import socket
import yaml
import base64

# --------------------------------------------------------
# Liest IP- und Port-Informationen aus der Konfigurationsdatei (config.yaml).
# Gibt – je nach Rolle (server oder client) – die entsprechenden Werte zurück.
# --------------------------------------------------------
def read_yaml_file(role: str) -> tuple[str, int]:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if role == "server":
        return config["server_ip"], int(config["server_port"])
    else:
        return config["client_ip"], int(config["client_port"])


# --------------------------------------------------------
# Fügt bei Bedarf fehlende Padding-Zeichen ('=') für Base32 hinzu.
# Base32-Daten müssen immer eine Länge haben, die durch 8 teilbar ist.
# Wenn das nicht der Fall ist, ergänzt diese Funktion automatisch '='-Zeichen.
# --------------------------------------------------------
def fix_base32_padding(encoded_str: str) -> str:
    missing_padding = len(encoded_str) % 8
    if missing_padding != 0:
        encoded_str += '=' * (8 - missing_padding)
    return encoded_str


# --------------------------------------------------------
# Wandelt empfangene DNS-ähnliche Nachrichten (Base32-kodiert)
# wieder in die ursprünglichen Binärdaten um.
# Beispiel für empfangene DNS-Pakete:
# "001.ABCD1234.domain.com"
# "002.XYZ98765.domain.com"
# --------------------------------------------------------
def decode_payload(dns_packets: list[str]) -> bytes:
    packet_dict = {}

    # Alle empfangenen Pakete durchlaufen und nach Nummer sortieren
    for packet in dns_packets:
        labels = packet.split('.')

        # Prüfen, ob das Paket korrekt formatiert ist
        if len(labels) < 4:
            continue

        # Die erste Komponente ist die Paketnummer (z. B. 001)
        packet_number = int(labels[0])

        # Entfernt die Nummer und die Domain-Endungen (.domain.com)
        # Übrig bleibt nur der Base32-Datenanteil
        base32_chunk = "".join(labels[1:-2])
        packet_dict[packet_number] = base32_chunk

    # Entfernt ein eventuelles Startpaket mit ID 0
    packet_dict.pop(0, None)

    # Sortiert die Pakete nach ihrer Nummer und fügt sie zu einem String zusammen
    full_base32_data = "".join(packet_dict[i] for i in sorted(packet_dict.keys()))

    # Korrigiert das Base32-Padding und dekodiert in Binärdaten
    padded_data = fix_base32_padding(full_base32_data)
    decoded_bytes = base64.b32decode(padded_data)

    return decoded_bytes


# --------------------------------------------------------
# Schreibt empfangene Binärdaten in eine Datei.
# Der Dateiname enthält IP und Port des sendenden Clients.
# --------------------------------------------------------
def save_received_file(file_path: str, data: bytes) -> None:
    with open(file_path, "wb") as file:
        file.write(data)
    print(f"\nDatei gespeichert: {file_path} ({len(data)} Bytes)")


# --------------------------------------------------------
# ---------------------- HAUPTPROGRAMM ---------------------
# --------------------------------------------------------

# Server-IP und Port aus der YAML-Konfigurationsdatei laden
server_ip, server_port = read_yaml_file("server")

# UDP-Socket erstellen und an Server-IP + Port binden
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind((server_ip, server_port))
print(f"UDP-Server läuft auf {server_ip}:{server_port}")
print("Warten auf eingehende Pakete...")

# Liste zum Speichern aller empfangenen DNS-ähnlichen Nachrichten
received_packets = []

try:
    while True:
        # Warten auf eingehende UDP-Nachrichten vom Client
        data, client_address = udp_server_socket.recvfrom(1024)
        message = data.decode(errors='ignore')
        print(f"Empfangen von {client_address}: {message}")

        # Nachricht zwischenspeichern
        received_packets.append(message)

        # Prüfen, ob das Endpaket ("EOF") empfangen wurde
        parts = message.split('.')
        if len(parts) > 1 and parts[1] == "EOF":
            # Bestätigung (ACK) an den Client senden
            udp_server_socket.sendto("ACK".encode(), client_address)
            print("EOF erkannt – Übertragung abgeschlossen.")
            break

    # Empfangene DNS-Pakete zu Binärdaten dekodieren
    decoded_data = decode_payload(received_packets)

    # Daten als Textdatei abspeichern
    #save_received_file(f"received_file_from_{client_address[0]}_{client_address[1]}.txt", decoded_data)
    # Wenn du eine Bilddatei überträgst, kannst du stattdessen:
    save_received_file(f"received_photo_from_{client_address[0]}_{client_address[1]}.jpg", decoded_data)

except Exception as error:
    # Fehlerbehandlung bei Netzwerk- oder Dekodierfehlern
    print("Fehler aufgetreten:", error)

finally:
    # Socket schließen, wenn der Server beendet wird
    udp_server_socket.close()
    print("Server beendet und Socket geschlossen.")
