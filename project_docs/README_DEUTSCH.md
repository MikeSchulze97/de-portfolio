# Data Engineering Portfolio – Batch Event Pipeline (IU)

Dieses Projekt ist eine **Data-Engineering-Prüfungsleistung** im Rahmen des Studiums an der IU.

Ziel des Projekts ist der Nachweis eines **konzeptionellen Verständnisses sowie der technischen Umsetzung einer vollständigen, batch-basierten Data Pipeline** – von der Ingestion bis zur Aggregation – unter Verwendung transparenter und reproduzierbarer Mechanismen.

Der Fokus liegt bewusst auf **grundlegenden Data-Engineering-Prinzipien** und nicht auf Performance, Skalierbarkeit oder Produktivbetrieb.

---

## Projektziel & Umfang

Dieses Projekt demonstriert:

- eine vollständige End-to-End-Batch-Pipeline
- eine klare Trennung von Ingestion, Verarbeitung und Aggregation
- eventzeitbasierte Datenverarbeitung
- explizites Zustandsmanagement über Checkpoints
- deterministische und reproduzierbare Ausführung

Das Projekt ist **kein Produktivsystem**.  
Alle Designentscheidungen sind bewusst vereinfacht, um **Nachvollziehbarkeit und Transparenz** zu gewährleisten – ein zentraler Aspekt im akademischen Kontext.

---

## Was in diesem Projekt ausgeführt wird

Die Pipeline besteht aus **zwei Arten von Komponenten**:

### Lang laufender Service
- **Ingestion Service (FastAPI)**  
  Nimmt Events per HTTP entgegen und speichert sie als rohe JSON-Dateien.

### Batch-Jobs
- **Batch Processing (`run_batch.py`)**  
  Verarbeitet rohe Events zu validierten, partitionierten Datensätzen.
- **Aggregation (`run_aggregate.py`)**  
  Aggregiert verarbeitete Events zu finalen Ergebnisdateien.

Alle Komponenten werden **ausschließlich über Docker und Docker Compose** ausgeführt.  
Eine lokale Python-Installation ist nicht erforderlich.

---

## Architekturübersicht

Die Pipeline folgt einer linearen, batch-orientierten Architektur:

CSV Input  
→ Event Generator  
→ Ingestion Service (FastAPI)  
→ `data/raw/`  
→ Batch Processing  
→ `data/processed/date=YYYY-MM-DD/hour=HH/`  
→ Aggregation  
→ `data/aggregated/`

Alle Zwischen- und Endergebnisse werden im lokalen Dateisystem gespeichert, um maximale Transparenz zu gewährleisten.

---

## Datenfluss

### Ingestion

- Events werden per HTTP POST an den Ingestion Service gesendet.
- Jedes Event wird **unverändert** als einzelne JSON-Datei gespeichert.
- In diesem Schritt findet **keine Transformation oder Validierung** statt.

Die Event-Zeit ist im Dateinamen kodiert.

Beispiel für einen Dateinamen:  
20260210T1015001234_ecommerce_transaction.json

---

### Batch Processing

Der Batch-Prozessor:

- liest rohe JSON-Eventdateien
- validiert Schema und Struktur
- extrahiert die Event-Zeit aus dem Dateinamen
- schreibt valide Events als JSON Lines (`events.jsonl`)
- partitioniert Daten nach `date=YYYY-MM-DD/hour=HH`
- verfolgt verarbeitete Dateien über einen expliziten Checkpoint

Behandelte Szenarien:

- ungültiges Schema → Quarantäne
- fehlerhaftes JSON → Quarantäne
- bereits verarbeitete Dateien → übersprungen
- verspätet eintreffende Events → korrekt in historische Partitionen einsortiert

Checkpoint-Datei:  
data/_checkpoints/processed_raw_files.txt

Rohe Daten werden **niemals verändert**.

---

### Aggregation

Der Aggregationsschritt:

- liest `events.jsonl` pro Partition
- aggregiert Events nach `event_type`
- schreibt Ergebnisse in `event_counts.json`
- verfolgt den Aggregationszustand über Änderungszeitstempel der Partitionen

State-Datei:  
data/_checkpoints/aggregated_partitions_state.json

Nur Partitionen mit neuen oder geänderten Daten werden neu berechnet, sofern nicht `--force` verwendet wird.

---

## Zustandsmanagement & Reproduzierbarkeit

Der Zustand der Pipeline wird explizit über Checkpoint-Dateien verwaltet.

Dies gewährleistet:

- idempotente Batch-Ausführung
- keine doppelte Verarbeitung
- deterministische Ergebnisse über mehrere Läufe hinweg
- sichere Wiederholbarkeit nach Neustarts

Die Pipeline kann jederzeit gestoppt, neu gestartet und erneut ausgeführt werden, ohne manuelle Bereinigung.

---

## Verzeichnisstruktur

data/
├── raw/
├── processed/
│   └── date=YYYY-MM-DD/
│       └── hour=HH/
│           └── events.jsonl
├── aggregated/
│   └── date=YYYY-MM-DD/
│       └── hour=HH/
│           └── event_counts.json
└── _checkpoints/
    ├── processed_raw_files.txt
    └── aggregated_partitions_state.json

---

## Ausführen und Testen der Pipeline (Docker)

Alle Interaktionen erfolgen über ein PowerShell-Hilfsskript.

Ingestion Service starten:  
.\tasks_docker.ps1 up

Swagger UI:  
http://localhost:8000/docs

Batch-Verarbeitung ausführen:  
.\tasks_docker.ps1 batch  
.\tasks_docker.ps1 batch -Limit 50

Verarbeitete Partitionen anzeigen:  
.\tasks_docker.ps1 partitions

Aggregation ausführen:  
.\tasks_docker.ps1 aggregate  
.\tasks_docker.ps1 aggregate -Force

Alle Container stoppen:  
.\tasks_docker.ps1 down

Mehrfache Ausführungen erzeugen keine Duplikate und berücksichtigen bestehende Checkpoints.

---

## Designentscheidungen (konzeptionelle Begründung)

- Batch-orientiertes Design zur Fokussierung auf deterministische Verarbeitung
- Dateisystembasierte Speicherung für maximale Transparenz
- Explizite Checkpoints statt impliziter Idempotenz
- Eventzeitbasierte Partitionierung zur korrekten Behandlung verspäteter Events
- Docker-basierte Ausführung für reproduzierbare und vergleichbare Ergebnisse

Diese Entscheidungen priorisieren **Klarheit, Nachvollziehbarkeit und konzeptionelle Korrektheit** gegenüber Skalierbarkeit oder Performance.

---

## Umfang & explizite Abgrenzung

Dieses Projekt schließt bewusst aus:

- Streaming-Plattformen (Kafka, Kinesis)
- verteilte Speichersysteme (S3, HDFS)
- Orchestrierungsframeworks (Airflow, Prefect)
- Schema-Registries
- Visualisierungs- oder BI-Layer

Der Umfang ist bewusst begrenzt, um **zentrale Konzepte des Batch Data Engineerings** in einer kontrollierten und transparenten Umgebung zu demonstrieren.