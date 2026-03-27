# Backend Developer Technical Assessment

A 3-service data pipeline using Docker, Flask, FastAPI, and PostgreSQL.

## Architecture

```
Flask Mock Server (port 5000)
        ↓  JSON data
FastAPI Pipeline (port 8000)
        ↓  upsert
PostgreSQL (port 5432)
```

## Prerequisites

- Docker Desktop (running)
- Docker Compose v2+

## Quick Start

```bash
# 1. Enter project directory
cd project-root

# 2. Build and start all services
docker-compose up -d --build

# 3. Verify all containers are running
docker-compose ps
```

## Testing Endpoints

### Flask Mock Server (port 5000)

```bash
# Health check
curl http://localhost:5000/api/health

# Get paginated customers
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Get single customer
curl http://localhost:5000/api/customers/CUST001
```

### FastAPI Pipeline Service (port 8000)

```bash
# Health check
curl http://localhost:8000/api/health

# Trigger data ingestion (run this first!)
curl -X POST http://localhost:8000/api/ingest

# Get paginated customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Get single customer from DB
curl http://localhost:8000/api/customers/CUST001
```

## API Interactive Docs

FastAPI provides auto-generated docs:
- Swagger UI: http://localhost:8000/docs


## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/
    │   └── customer.py
    ├── services/
    │   └── ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Teardown

```bash
docker-compose down          # stop containers
docker-compose down -v       # stop + remove volumes (wipes DB)
```
