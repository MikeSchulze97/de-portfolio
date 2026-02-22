PROJECT STATE SNAPSHOT

Data Engineering Portfolio – IU Prüfungsleistung
Status: Architecture, Logic & Structure Frozen

1) PROJEKTKONTEXT & RAHMENBEDINGUNGEN (UNVERHANDELBAR)
Ziel

Dieses Projekt ist eine IU-Prüfungsleistung im Bereich Data Engineering. Ziel ist der Nachweis von Konzeptverständnis und technischer Umsetzung einer vollständigen Data Pipeline von Datenquelle bis Aggregation.

Das Projekt ist kein Produktivsystem, kein Skalierungsprojekt und kein Optimierungsprojekt.

IU-relevante Anforderungen (abstrahiert)

End-to-End-Pipeline mit klarer Datenflusslogik

Trennung von Ingestion, Verarbeitung und Aggregation

Batch-orientierte Verarbeitung

Nachvollziehbarkeit und Reproduzierbarkeit

Verständliche Dokumentation der Architektur

Keine Blackbox-Lösungen

Bereits abgegebene / festgelegte Inhalte (FIX)

Grundkonzept der Pipeline (CSV → Events → Batch → Aggregation)

Architekturidee und Darstellung

Entscheidung für dateibasierte Speicherung und Batch-Verarbeitung

Diese Inhalte dürfen nicht neu interpretiert, umgedeutet oder ersetzt werden.

Abgrenzung & Prioritätsregeln

Feststehend (höchste Priorität)

Architekturprinzip

Datenflusslogik

Ordner- und Verantwortungsstruktur

Docker-basierte Ausführung

Nachrangig / offen

Textliche Erläuterungen (README)

Formulierungen für Abgabe

Im Zweifel gilt: Code + Architektur > README > Chat-Interpretationen.

2) ARCHITEKTUR & SYSTEMSTRUKTUR (ARCHITECTURE FREEZE)
Gesamtarchitektur (IST-ZUSTAND)

CSV-Datei (Input)
→ Event Generator (Docker, Python)
→ Ingestion Service (FastAPI, Docker)
→ Raw Storage (JSON Files)
→ Batch Processing (Docker)
→ Processed Storage (partitioniert)
→ Aggregation (Docker)
→ Aggregated Results

Existierende Komponenten (FIX)

Event Generator
Simuliert Events aus einer CSV-Datei und sendet diese per HTTP.

Ingestion Service
Nimmt Events entgegen und speichert sie unverändert als Raw-Events.

Batch Processing
Verarbeitet Raw-Events batchweise zu Processed-Events unter Nutzung von Checkpoints.

Aggregation
Aggregiert Processed-Events zustandsbasiert (nur neue/aktualisierte Partitionen).

Storage Layer (Dateisystem)

raw

processed

aggregated

_checkpoints

Docker / Docker Compose
Einzige vorgesehene Ausführungsumgebung.

PowerShell Task-Skripte
Einzige vorgesehene Bedien- und Steuerungsschnittstelle.

Fixe Architekturentscheidungen (NICHT ÄNDERN)

Keine Datenbank

Keine Streaming-Frameworks

Keine Message Queues

Keine Cloud-Services

Batch-Verarbeitung ist konzeptionell gewollt

Dateibasierte Speicherung ist konzeptionell gewollt

Checkpoints sind Pflichtbestandteil der Logik

Erweiterbarkeit (eng begrenzt)

Erlaubt sind nur additive Erweiterungen, die:

keine bestehenden Komponenten ersetzen

keine Ordnerstruktur verändern

keine Datenflüsse umleiten

3) CODE-STRUKTUR (ABSTRAKT, VERBINDLICH)
Projekt-Root-Struktur (FIX)

de-portfolio/
│
├── data/
│   ├── input/            # CSV-Datenquelle (FIX)
│   ├── raw/              # rohe Events (JSON)
│   ├── processed/        # partitionierte Events (date/hour)
│   ├── aggregated/       # Aggregationsergebnisse
│   └── _checkpoints/     # Zustände & Idempotenz
│
├── services/
│   ├── ingestion/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── event-generator/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── processing/
│       ├── run_batch.py
│       ├── run_aggregate.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── docker-compose.yml
├── tasks_docker.ps1
├── README.md
└── venv/

Modulverantwortlichkeiten (EINDEUTIG)

event-generator/app.py

Liest CSV aus data/input

Erzeugt Event-Objekte

Sendet Events per HTTP

Keine Speicherung

ingestion/app.py

Nimmt HTTP-Events entgegen

Schreibt exakt ein Event = eine JSON-Datei

Keine Transformation

run_batch.py

Liest Raw-Events

Nutzt Checkpoints zur Idempotenz

Schreibt partitionierte Processed-Events

Darf Raw-Daten niemals verändern

run_aggregate.py

Liest Processed-Events

Aggregiert zustandsbasiert

Überschreibt nur eigene Aggregationsergebnisse

tasks_docker.ps1

Orchestriert alle Abläufe

Gilt als „öffentliche API“ für Bedienung

docker-compose.yml

Definiert alle Services, Volumes, Netzwerke

Änderungen nur nach expliziter Entscheidung

4) AKTUELLER ARBEITSSTAND (EINGEFROREN)
Funktionsstatus

Pipeline funktioniert End-to-End

Generator → Ingestion → Raw → Batch → Processed → Aggregation

Checkpoints funktionieren korrekt

Wiederholte Läufe erzeugen keine Duplikate

Aggregation ist zustandsbasiert

Verifiziert durch

Mehrfache Docker-Neustarts

Wiederholte Batch- und Aggregate-Runs

Manuelle Kontrolle der Outputs

Aktueller Fokus

Projekt einfrieren

Abgabe vorbereiten

Dokumentation finalisieren

Explizit nicht Teil des Fokus

Performance

Parallelisierung

Architektur-Vergleiche

Technologie-Wechsel

5) VERBINDLICHE ARBEITSREGELN FÜR ZUKÜNFTIGE CHATS

Diese Regeln sind bindend:

Keine strukturellen Änderungen ohne explizite Rückfrage

Kein Refactoring, keine Optimierung, keine „Verbesserungen“

Kein Austausch von Technologien oder Paradigmen

Bestehender Code darf nur angepasst werden, wenn:

der vollständige Code vorliegt

der Zweck der Änderung klar benannt ist

Keine Annahmen bei fehlendem Kontext

Bei Unklarheit: nachfragen, nicht interpretieren

Bestehende Entscheidungen haben Vorrang vor Alternativen

Dieser Snapshot überstimmt jede Chat-Vermutung

ENDE DES PROJECT STATE SNAPSHOTS