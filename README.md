# **Anleitung und Beschreibung – DNS-Tunnel-Projekt**

## Hintergrund

Das **Domain Name System** (**DNS**) übersetzt Domainnamen (z. B. ```example.com```) in IP-Adressen, damit Computer im Internet miteinander kommunizieren können.
Da DNS fast überall erlaubt und in Firewalls selten blockiert wird, nutzen Angreifer manchmal sogenannte **DNS-Tunnel**, um Daten versteckt über DNS-Anfragen zu übertragen.

Dieses Projekt demonstriert das Prinzip in einer **sicheren**, **lokalen Laborumgebung**, ohne echte DNS-Server oder Internetverbindungen zu verwenden.
Ziel ist es, die Funktionsweise dieser Technik zu verstehen und mögliche Sicherheitsrisiken besser einschätzen zu können.

## Projektbeschreibung

Datenübertragung zwischen einem Client und einem Server über das UDP-Protokoll.
Die Anwendung dient ausschließlich zu **Lern- und Demonstrationszwecken** und ist nicht für **produktive oder sicherheitskritische Nutzung** vorgesehen.

Ein DNS-Tunnel erlaubt es, Daten innerhalb scheinbar normaler DNS-Anfragen zu übertragen.
In diesem Projekt wird das Prinzip **legal und sicher im lokalen Netzwerk** demonstriert.

## Installation

### Voraussetzungen

- Python 3.9 oder höher

- Installierte Abhängigkeiten aus ```requirements.txt```

### Installation der Module

```bash
pip install -r requirements.txt
```

**Beispiel ```config.yaml```**

```yaml
server_ip: "127.0.0.1"
server_port: 5353

client_ip: "127.0.0.1"
client_port: 5000
```

*Stelle sicher, dass Server und Client dieselbe IP-Adresse (**127.0.0.1**) verwenden.
Die IP kann auch eine echte Netzwerkadresse sein (z. B. 192.168.1.10)*.

## Verwendung

### 1. Server starten

Auf dem Empfänger-Rechner (oder zuerst im Terminal):

```bash
python dns-tunnel-server.py
```

**Beispielausgabe**:

```bash
UDP-Server läuft auf 127.0.0.1:5353
Warten auf eingehende Pakete...
```

### 2. Client starten

Auf dem Sender-Rechner (oder zweites Terminalfenster):

```bash
python dns-tunnel-client.py
```

**Beispielausgabe**:

```bash
Gesendet: 001.IRUWKICLOVXHG5BAMRSXGICLOJUWKZ3FOMQOFAETEBIGQ2LMN5ZW64DINFSSYIC.TORZGC5DFM5UWKIDVNZSCA6TFNF2GY33TMUQFOZLJONUGK2LUBUFOFAE6IRUWKI.CLOVXHG5BAMRSXGICLOJUWKZ3FOPRIBHBAOZXW4ICTOVXCAVD2OUQGS43UEB3WK.2LUEBWWK2DSEBQWY4ZAMVUW4IDNNFWG.domain.com
Gesendet: 002.S5GDURZGS43DNBSXGICIMFXGIYTVMNUC4ICFOMQGS43UEBSWS3RAOBUGS3DPONX.XA2DJONRWQZLTEBLWK4TLFQQGIYLTEBZWK2LUEDB3YYTFOIQHU53FNFSWS3TIMF.WGE5DBOVZWK3TEEBFGC2DSMVXCATLFNZZWG2DFNYQGS3RAI3B3Y2DSOVXGOLBAK.N2HEYLUMVTWSZJAOVXGIICLN5XGM3DJ.domain.com
.
.
.
Gesendet: 000.EOF.domain.com
Antwort vom Server ('127.0.0.1', 5353): ACK
Verbindung geschlossen.
```

## Funktionsweise im Detail

### 1. Kodierung

Der Client:

- liest z. B. eine Datei aus dem ```data/```-Verzeichnis

- kodiert deren Inhalt mit **Base32**,

- zerlegt die Daten in kleine Stücke (max. 220 Zeichen),

- erstellt daraus DNS-ähnliche Abfragen (z. B. ```001.ABCD1234.domain.com```).

### 2. Übertragung

Die Abfragen werden per **UDP-Socket** an den Server gesendet.
UDP eignet sich, da es verbindungslos und leichtgewichtig ist, ähnlich wie DNS selbst.

### 3. Empfang

Der Server:

- empfängt die UDP-Pakete

- sammelt sie, bis das Paket mit EOF eintrifft,

- fügt die Datenpakete wieder zusammen,

- dekodiert sie aus Base32 zurück in Binärdaten,

- und speichert die Datei lokal ab.


## Sicherheits- und Testhinweise

- Dieses Projekt **emuliert DNS-Tunneling**, nutzt aber **kein echtes DNS-Protokoll**.

- Es dient **ausschließlich zu Demonstrations- und Lerneffekten**.

- Kein echter DNS-Server oder externer Resolver wird kontaktiert.

- Tests sollten **lokal oder in einem geschützten Laborumfeld** erfolgen.

- Der Netzwerkverkehr kann mit Tools wie **Wireshark** beobachtet werden (Filter: ```udp.port == 5353```).



## Technische Details

| Funktion                      | Zweck                                                      |
| ----------------------------- | ---------------------------------------------------------- |
| `read_yaml_file()`            | Liest IP- und Port-Konfigurationen aus YAML-Datei          |
| `generate_base32_payload()`   | Kodiert Binärdaten in Base32-Strings                       |
| `split_payload_into_chunks()` | Zerlegt Base32-String in übertragbare UDP-Pakete           |
| `create_dns_labels()`         | Baut DNS-konforme Labels (≤ 63 Zeichen)                    |
| `build_dns_queries()`         | Erzeugt DNS-artige Query-Namen (z. B. 001.data\.domain.com) |
| `decode_payload()`            | Fügt empfangene Pakete zusammen und dekodiert sie          |
| `save_received_file()`        | Speichert die empfangenen Binärdaten als Datei             |

## Testleitfaden

### 1. Server starten

```
python dns-tunnel-server.py
```

### 2. Client starten

```
python dns-tunnel-client.py
```

### 3. Netzwerkverkehr beobachten (optional)

- Öffne Wireshark

- Filter: ```udp.port == 5353```

- Du siehst Base32-Daten in DNS-ähnlichen Paketen

### 4. Überprüfung der empfangenen Datei

- Auf dem Server erscheint:

```
received_file_from_<clientip>_<port>.jpg
```

- Inhalt sollte mit Originaldatei übereinstimmen

## Erweiterungsmöglichkeiten

- Implementierung eines echten DNS-Headers (z. B. mit ```dnslib```)

- Einbau eines Wiederholungsmechanismus bei Paketverlust

- Datenkompression vor Base32-Kodierung (z. B. mit ```zlib```)

- Verschlüsselung des Payloads (z. B. AES oder Fernet)

- Fortschrittsanzeige im Client (z. B. über ```tqdm```)

- Logging und Statistik über übertragene Bytes

## Beispielergebnis

Nach erfolgreicher Übertragung liegt im Serververzeichnis eine Datei wie:

```bash
received_file_from_127.0.0.1_5000.txt
```

**Beispielausgabe Server**:

```bash
UDP-Server läuft auf 127.0.0.1:5353
Warten auf eingehende Pakete...
Empfangen von ('127.0.0.1', 5000): 001.MFRGGZDFMZTWQ2LLNR...
Empfangen von ('127.0.0.1', 5000): 002.MZXXE3DPEB2GQYLONR...
Empfangen von ('127.0.0.1', 5000): 000.EOF.domain.com
EOF erkannt – Übertragung abgeschlossen.

Datei gespeichert: received_file_from_127.0.0.1_5000.txt (124 Bytes)
Server beendet und Socket geschlossen.
```

## Bekannte Einschränkungen

- Keine echte DNS-Protokollstruktur (nur Simulation über UDP).

- Kein Wiederholungsmechanismus bei Paketverlust.

- Base32-Kodierung vergrößert Datenvolumen um ca. 60 %.

- Nur kleine bis mittlere Dateien getestet (Text, Bild)

## Fazit

Dieses Projekt zeigt auf einfache und nachvollziehbare Weise, wie Daten in DNS-ähnlichen Nachrichten versteckt und über UDP gesendet werden können.

Es verdeutlicht:

- das Prinzip von **DNS-Tunneling**,

- die Bedeutung von **Paketstruktur und Kodierung**,

- und die **Sicherheitsrisiken** solcher Techniken im realen Netzwerkverkehr.
