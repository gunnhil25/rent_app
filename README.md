# 🏠 Household Finance Tracker WebApp

A modern household rent and shared expense tracking web application with a **FastAPI (Python 3.12)** backend and **PostgreSQL 16** database, fully containerized with **Docker** for deployment on Proxmox LXC, homeservers, or local environments.

---

## 🚀 Quick Start (Docker Compose)

The easiest way to run the application is with Docker Compose:

```bash
# 1. Clone or copy this repository to your server/LXC
cd "Rent App"

# 2. (Optional) Customize passwords or port in .env
cp .env.example .env

# 3. Build and launch the containers
docker compose up -d --build
```

Once running:
* **Web Application:** `http://<YOUR_SERVER_IP>:8000/`
* **Interactive API Docs (Swagger UI):** `http://<YOUR_SERVER_IP>:8000/docs`
* **Database Health Check:** `http://<YOUR_SERVER_IP>:8000/api/health`

---

## 📦 Proxmox LXC Deployment Guide

### Option A: Standard Docker inside an LXC Container
If you are running Docker inside a Proxmox LXC container (e.g. Debian or Ubuntu template):

1. **Ensure your LXC container supports Docker:**
   - In Proxmox VE Web UI: go to **LXC Container** → **Options** → **Features**
   - Enable **`nesting=1`** and **`keyctl=1`** (required for Docker inside LXC).
2. **Install Docker in the LXC** (if not already installed):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```
3. **Deploy the App:**
   ```bash
   git clone <your-repo> /opt/rent-app
   cd /opt/rent-app
   docker compose up -d
   ```
4. **Auto-start on LXC boot:**
   Docker Compose containers with `restart: unless-stopped` will automatically start whenever your LXC boots up.

---

## 🛠️ Architecture & Features

```
┌────────────────────────────────────────────────────────┐
│                   Proxmox LXC Container                │
│                                                        │
│   ┌───────────────────────┐   ┌────────────────────┐   │
│   │     rent_app_web      │   │    rent_app_db     │   │
│   │     (FastAPI 3.12)    │   │  (Postgres 16)     │   │
│   │                       │   │                    │   │
│   │  • Serves Frontend    │◄──┼─► • Relational DB  │   │
│   │  • REST API endpoints │   │   • Named Volume   │   │
│   │  • Atomic /api/data   │   │     Persistence    │   │
│   └──────────▲────────────┘   └────────────────────┘   │
└──────────────┼─────────────────────────────────────────┘
               │ Port 8000
        ┌──────┴──────┐
        │   Browser   │
        └─────────────┘
```

* **Backend:** FastAPI with `asyncpg` and SQLAlchemy 2.0.
* **Database:** PostgreSQL 16 Alpine with persistent volume `rent_app_postgres_data`.
* **Frontend:** Glassmorphism UI with Dark/Light theme, monthly spending trends, category donuts, settlement balance calculation, and category filtering & sorting.
* **Full Persistence:** All members, categories, and transactions are stored in PostgreSQL.
* **Zero-Setup Seeding:** Automatically seeds default household categories (Rent, Groceries, Utilities, etc.) if the database is fresh.

---

## 🗄️ Database Management & Backups

### Creating a Database Backup
```bash
docker exec -t rent_app_db pg_dump -U rentapp household_tracker > backup_$(date +%F).sql
```

### Restoring from Backup
```bash
cat backup_2026-10-22.sql | docker exec -i rent_app_db psql -U rentapp household_tracker
```

### In-App Data Export/Import
You can also back up or transfer your data at any time directly through the web UI under **Settings → Data Management** (Export JSON / Export CSV / Import JSON).

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web application UI |
| `GET` | `/api/health` | Backend & database health check |
| `GET` | `/api/data` | Fetch complete household state |
| `POST` | `/api/data` | Synchronize full state atomically |
| `GET` | `/api/members` | List household members |
| `POST` | `/api/members` | Add new member |
| `DELETE` | `/api/members/{name}` | Remove member and their transactions |
| `GET` | `/api/categories` | List expense categories |
| `POST` | `/api/categories` | Create new category |
| `PUT` | `/api/categories/{name}` | Update category icon/color |
| `DELETE` | `/api/categories/{name}` | Delete category |
| `GET` | `/api/expenses` | List/filter transactions (query by category, payer, sort) |
| `POST` | `/api/expenses` | Record a new expense or income |
| `PUT` | `/api/expenses/{id}` | Edit a transaction |
| `DELETE` | `/api/expenses/{id}` | Delete a transaction |
