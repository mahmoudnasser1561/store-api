# Store API (Flask + Postgres) — Retail Backend (Amazon-like)

A production-style REST API for managing **Stores**, **Items**, and **Tags** — with **JWT authentication**, **schema validation**, **migrations**, and **OpenAPI/Swagger docs**.

> Built as a portfolio backend project to demonstrate real-world API design, entity relationships, and containerized local development.

---

## Features

- **Stores / Items / Tags** domain (Retail logic)
- **Link/Unlink Items ↔ Stores**
- **Tag Items** (many-to-many)
- **Store search** and **store item count**
- **JWT Authentication** (access + refresh + logout)
- **Validation & serialization** via schemas (Flask-Smorest)
- **Error handling** (consistent API errors)
- **PostgreSQL** persistence
- **Database migrations** (Alembic/Flask-Migrate)
- **OpenAPI 3.0 + Swagger UI** generated automatically

---

## Tech Stack

- Python 3.12 (Flask)
- Flask-Smorest (OpenAPI + Blueprints)
- SQLAlchemy + Flask-Migrate (Alembic)
- PostgreSQL 16
- Docker + Docker Compose

---

## Architecture

- `api` service: Flask REST API (port **5000**)
- `db` service: PostgreSQL 16 with init script + persistent volume

---

## API Documentation (Swagger / OpenAPI)

After running the stack:

- Swagger UI: `http://localhost:5000/swagger-ui`
- OpenAPI JSON: `http://localhost:5000/openapi.json`

The API is titled **“Stores REST API”** and versioned as **v1**.


## Quickstart (Docker)

### 1) Configure environment
Create a `.env` file

```env
DB_USER=flask
DB_PASSWORD=pass
DB_NAME=storeitem
DB_HOST=db
DB_PORT=5432
```

### 2) Run
Create a `.env` file

```bash
docker compose up --build
```

### 3) Open Swagger

Go to: ```http://localhost:5000/swagger-ui```


## Domain Model (Conceptual)

Store has many Items

Store has many Tags

Item ↔ Tag is many-to-many (junction table)

Mermaid ERD (conceptual):
<br> 
[![store_api ERD](screenshots/store_api.drawio.png)](screenshots/store_api.drawio.png)


## Example API Flow (using Swagger)

- Register → Login (get access_token, refresh_token)

- Create a store (POST /store)

- Create items (POST /item)

- Link an item to a store (PUT /store/{store_id}/item/{item_id})

- Create tags under a store (POST /store/{store_id}/tag)

- Tag an item (POST /item/{item_id}/tag/{tag_id})

- Swagger is the source of truth for request/response bodies.

##  Main Endpoints (Highlights)

#### Items

- GET /item

- POST /item

- GET /item/{item_id}

- PUT /item/{item_id}

- DELETE /item/{item_id}

#### Stores

- GET /store

- POST /store

- GET /store/{store_id}

- PUT /store/{store_id}

- DELETE /store/{store_id}

- GET /store/search

- GET /store/{store_id}/count

- PUT /store/{store_id}/item/{item_id} (link)

- DELETE /store/{store_id}/item/{item_id} (unlink → “Unassigned” behavior)

#### Tags

- GET /store/{store_id}/tag

- POST /store/{store_id}/tag

- GET /tag

- GET /tag/{tag_id}

- POST /item/{item_id}/tag/{tag_id}

- DELETE /item/{item_id}/tag/{tag_id}

#### Users / Auth

- POST /register

- POST /login

- POST /refresh

- POST /logout

- GET /user/{user_id}

- DELETE /user/{user_id}

## Project Structure
.
├── app.py               # App factory + config + blueprint registration
├── resources/           # Flask-Smorest blueprints (routes)
├── models/              # SQLAlchemy models
├── schemas.py           # Request/response schemas
├── migrations/          # Alembic migrations
├── db/                  # Postgres init script + Dockerfile
├── docker-compose.yaml  # Local stack
└── Dockerfile           # API container
