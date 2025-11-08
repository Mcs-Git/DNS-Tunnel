import socket
import yaml
import base64
import re

# --------------------------------------------------------
# Liest IP- und Port-Informationen aus der Konfigurationsdatei (config.yaml).
# Gibt je nach Parameter ("server" oder "client") die passende IP und Port zurück.
# --------------------------------------------------------
def read_yaml_file(role: str) -> tuple[str, int]:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if role == "server":
        return config["server_ip"], int(config["server_port"])
    else:
        return config["client_ip"], int(config["client_port"])


# --------------------------------------------------------
# Lädt die IP- und Port-Informationen des Servers aus der YAML-Datei.
# --------------------------------------------------------
server_ip, server_port = read_yaml_file("server")

# --------------------------------------------------------
# Erstellt einen UDP-Socket, der für den Versand der DNS-Pakete genutzt wird.
# --------------------------------------------------------
udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --------------------------------------------------------
# Globale Listen zur Zwischenspeicherung:
# - encoded_chunks: enthält die Base32-kodierten Datenstücke (in DNS-kompatiblen Labels)
# - dns_queries: enthält die finalen DNS-ähnlichen Abfragen, die gesendet werden
# --------------------------------------------------------
encoded_chunks = []
dns_queries = []


# --------------------------------------------------------
# Wandelt die Base32-kodierten Datenstücke in DNS-artige Abfragen um.
# Beispielausgabe: "001.ABCD1234.domain.com"
# Jede Abfrage erhält eine laufende ID (z. B. 001, 002, 003 ...).
# Am Ende wird ein "EOF"-Paket angehängt, um das Ende der Übertragung zu markieren.
# --------------------------------------------------------
def build_dns_queries(data_chunks: list[str]) -> list[str]:
    query_id = 1
    for chunk in data_chunks:
        query = f"{query_id:03}.{chunk}.domain.com"
        dns_queries.append(query)
        query_id += 1

    # Markiere das letzte Paket als "EOF" (End Of File)
    dns_queries.append("000.EOF.domain.com")
    return dns_queries


# --------------------------------------------------------
# Base32-kodiert die übergebenen Binärdaten und entfernt alle
# Sonderzeichen, damit sie DNS-konform verwendet werden können.
# --------------------------------------------------------
def generate_base32_payload(raw_data: bytes) -> str:
    encoded_bytes = base64.b32encode(raw_data)
    # Entferne unerwünschte Zeichen und b''-Notation
    cleaned = re.sub(r'[^A-Za-z0-9]+', '', encoded_bytes.decode())
    return cleaned


# --------------------------------------------------------
# Überprüft, ob die Länge eines DNS-Pakets zulässig ist.
# - DNS erlaubt pro Label maximal 63 Zeichen.
# - Gesamtgröße einer Abfrage sollte unter 255 Zeichen bleiben.
# --------------------------------------------------------
def check_query_length(packet: str) -> bool:
    return len(packet) <= 220


# --------------------------------------------------------
# Teilt einen langen Base32-String in handliche Teilstücke (Chunks) auf.
# Jedes Teilstück ist maximal 220 Zeichen lang.
# --------------------------------------------------------
def split_payload_into_chunks(payload: str) -> list[str]:
    if not check_query_length(payload):
        chunked = [payload[i:i+220] for i in range(0, len(payload), 220)]
        return chunked
    else:
        return [payload]


# --------------------------------------------------------
# Teilt jeden Daten-Chunk in DNS-konforme Labels auf (je maximal 63 Zeichen).
# Jedes Label wird durch einen Punkt getrennt.
# Beispiel: "ABCDEFGH..." → "ABC.DEF.GH..."
# --------------------------------------------------------
def create_dns_labels(payload_chunks: list[str]) -> list[str]:
    for chunk in payload_chunks:
        dns_label = '.'.join([chunk[i:i+63] for i in range(0, len(chunk), 63)])
        encoded_chunks.append(dns_label)
    return encoded_chunks


# --------------------------------------------------------
# Sendet alle generierten DNS-Abfragen an den Server über UDP.
# --------------------------------------------------------
def send_dns_packets() -> None:
    build_dns_queries(encoded_chunks)  # Baue DNS-Abfragen aus den Chunks
    for query in dns_queries:
        udp_client_socket.sendto(query.encode(), (server_ip, server_port))
        print(f"Gesendet: {query}")


# --------------------------------------------------------
# Liest eine Datei, Base32-kodiert deren Inhalt und teilt sie in
# DNS-kompatible Pakete auf, die anschließend gesendet werden können.
# --------------------------------------------------------
def prepare_file_for_transfer(file_path: str) -> None:

    with open(file_path, "rb") as file:
        file_content = file.read()
        payload = generate_base32_payload(file_content)
        payload_chunks = split_payload_into_chunks(payload)
        create_dns_labels(payload_chunks)


# --------------------------------------------------------
# ---------------------- HAUPTPROGRAMM ---------------------
# --------------------------------------------------------

# Liste mit zu sendenden Dateien
files = ["data/file.txt","data/photo.jpg"]

# Datei(en) vorbereiten (hier nur die erste aktiv)
prepare_file_for_transfer(files[1])
#prepare_file_for_transfer(files[1])  # Zweite Datei kann bei Bedarf aktiviert werden

try:
    print(f"Sende Datei: {files[0]}")
    # DNS-Pakete senden
    send_dns_packets()

    # Auf Antwort (ACK) des Servers warten
    response_data, server_address = udp_client_socket.recvfrom(1024)
    print(f"Antwort vom Server {server_address}: {response_data.decode()}")

except Exception as error:
    # Fehler beim Senden oder Empfangen behandeln
    print("Fehler aufgetreten:", error)

finally:
    # Socket schließen, um Ressourcen freizugeben
    udp_client_socket.close()
    print("Verbindung geschlossen.")
