# VoltEdge Charging Session Service

## Overblik
VoltEdge Charging Session Service er en microservice der håndterer realtids-telemetri fra elbil-ladestandere, detekterer anomalier og opretter incidents automatisk. Løsningen adresserer udfordring A4.3 (skalering og driftsstabilitet) og A4.2 (fragmenteret datamodel og begrænset analyseevne) fra VoltEdge Mobility A/S casen.

## Arkitektur
Løsningen er bygget med Domain Driven Design (DDD) og består af følgende bounded contexts:

- **Telemetriindsamling** — modtager og validerer telemetri fra ladestandere
- **Anomalidetektion** — analyserer telemetri og detekterer anomalier
- **Incidentoprettelse** — opretter og klassificerer incidents baseret på anomalier
- **Incidenteskalering** — håndterer eskalering og løsning af incidents

## Tech Stack
- **API** — Python 3.12, FastAPI
- **Database** — MySQL 8.0
- **Overvågning** — Prometheus + Grafana
- **Container** — Docker + Docker Compose
- **CI/CD** — GitHub Actions + GitHub Container Registry

## Mappestruktur
voltedge/charging-session-service/
├── app/
│   ├── api/                    # API endpoints (routers)
│   │   ├── telemetry_router.py
│   │   ├── incident_router.py
│   │   └── analytics_router.py
│   ├── domain/                 # Forretningslogik (DDD)
│   │   ├── telemetry.py        # Value objects + TelemetryStream aggregat
│   │   ├── anomaly.py          # Anomaly aggregat
│   │   ├── incident.py         # Incident entitet + SLADeadline value object
│   │   ├── charger.py          # ChargerDevice aggregat
│   │   ├── technician.py       # Technician entitet
│   │   └── events.py           # Domain events
│   ├── infrastructure/         # Database og repositories
│   │   ├── database.py
│   │   └── incident_repository.py
│   └── tests/                  # Unit tests
│       └── test_rule_engine.py
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
└── .env.example

## Kom i gang

### Krav
- Docker Desktop
- Git
- make

### Installation
1. Klon repo
```bash
git clone https://github.com/jonasboegh11/Eksamen.git
cd Eksamen
```

2. Opret `.env` fil
```bash
cp voltedge/charging-session-service/.env.example voltedge/charging-session-service/.env
```
Udfyld `.env` med dine værdier.

3. Start løsningen
```bash
make up
```

### Kommandoer
```bash
make up       # start alle services
make down     # stop alle services
make restart  # genstart alle services
make logs     # se logs
make clean    # stop + slet database
```

## API Endpoints

### Telemetri
| Method | Endpoint | Beskrivelse |
|--------|----------|-------------|
| POST | /telemetry/ | Send telemetri fra ladestandere |

### Incidents
| Method | Endpoint | Beskrivelse |
|--------|----------|-------------|
| GET | /incidents/ | Hent alle incidents |
| GET | /incidents/?severity=critical | Filtrer på severity |
| GET | /incidents/?charger_id=CHARGER-001 | Filtrer på lader |
| GET | /incidents/{id} | Hent specifikt incident |

### Analytics
| Method | Endpoint | Beskrivelse |
|--------|----------|-------------|
| GET | /analytics/summary | Samlet overblik |
| GET | /analytics/incidents-per-severity | Incidents fordelt på severity |
| GET | /analytics/incidents-per-charger | Incidents fordelt på lader |
| GET | /analytics/most-problematic-charger | Mest problematiske lader |

### System
| Method | Endpoint | Beskrivelse |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /metrics | Prometheus metrics |
| GET | /docs | Swagger UI dokumentation |

## Overvågning
| Service | URL | Beskrivelse |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI service |
| Swagger UI | http://localhost:8000/docs | API dokumentation |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboards |

Grafana indeholder to dashboards:
- **VoltEdge — Teknisk overvågning** — API svartider, requests og fejlrate
- **VoltEdge — BI Dashboard** — incidents per lader, per severity og over tid

## Tests
```bash
cd voltedge/charging-session-service
pytest app/tests/ -v
```

## CI/CD
Pipelinen kører automatisk ved push til main:
1. **detect-secrets** — scanner for passwords og API keys
2. **build-and-test** — kører unit tests og bygger Docker image
3. **deploy** — pusher Docker image til GitHub Container Registry

## DDD Objekter
| Type | Klasse | Beskrivelse |
|------|--------|-------------|
| Aggregat | ChargerDevice | Samler telemetri og incidents for én lader |
| Aggregat | TelemetryStream | Håndterer telemetri-strøm og events |
| Aggregat | Anomaly | Detekterer og klassificerer anomalier |
| Entitet | Incident | Unik hændelse med status og SLA deadline |
| Entitet | Technician | Tekniker der kan tildeles incidents |
| Value Object | MeasurementValue | Immutable måling (kW, volt, ampere) |
| Value Object | SLADeadline | Beregnet deadline baseret på severity |
| Domain Service | rule_engine | Evaluerer telemetri mod regler |