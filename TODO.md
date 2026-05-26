# VoltEdge Charging Session Service — TODO

## API
- [x] GET endpoints til at hente incidents
- [x] Analytics endpoint (incidents per lader, per severity)

## DDD
- [x] Charger som aggregat med metoder i Python koden
- [x] Incident som entitet med unikt id i Python koden
- [x] Telemetry som value object i Python koden
- [x] Anomaly som aggregat med events i Python koden
- [x] Technician som entitet i Python koden
- [x] Domain events der matcher event storming diagram
- [ ] Klassediagram der matcher Python koden

## DevSecOps
- [x] CI/CD pipeline i GitHub Actions (build + test)
- [x] Detect secrets i GitHub Actions
- [x] CD pipeline med GitHub Container Registry
- [x] Unit tests på regelmotoren

## Overvågning — A4.3
- [x] Prometheus (samler metrics fra API'et)
- [x] Grafana dashboard 1 — teknisk overvågning (API svartider, fejlrate, database performance)

## BI — A4.2
- [x] Grafana dashboard 2 — forretningsdata (incidents per lader, per severity, over tid)

## Machine Learning — A4.2
- [ ] Predictive incident service (forudsig fejl baseret på historisk telemetri)

## Dokumentation
- [ ] README fyldestgørende med setup, arkitektur og hvordan man kører projektet
- [ ] Klassediagram der matcher Python koden