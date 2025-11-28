## COMP 3005 – Database Management Systems Final Project

A console-based management system for a health and fitness club, built with Python and PostgreSQL using SQLAlchemy ORM.

### Video Demo

Link to demo: TBA

### Project Structure

- `app/`
  - `main.py`: Application entry, login/register routing based on role
  - `member.py`: Member workflows (dashboard, metrics, goals, sessions)
  - `trainer.py`: Trainer workflows and scheduling
  - `admin.py`: Admin workflows (rooms, equipment, billing)
  - `cli_utils.py`: Console UI helpers
- `models/`
  - `models.py`: SQLAlchemy ORM models (User, Role, Metric, Goal, Schedule, Session, Billing, etc.)
  - `__init__.py`: Model exports
- `docs/`
  - `database_creation.txt`: SQL to create and seed the database
  - `ERD.pdf`: Entity-Relationship diagram
  - `report.tex` / `report.pdf`: Project report
- `setup.sh`: Optional helper to bootstrap venv, dependencies, and database

### Prerequisites

- Python 3.10+
- PostgreSQL
- pip

### Environment Configuration

The app reads the database URL from `.env` using `python-dotenv`.

1. Create a file named `.env` in the project root with:

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

### Install Dependencies

Recommended: use a virtual environment.

```
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Database Setup

```
# Ensure your DATABASE_URL points to an existing server and a DB you can modify
psql -U <user> -h <host> -d <db> -f docs/database_creation.txt
```

Option B: Use `setup.sh` which will prompt for host/user/password and create/seed the DB:

```
bash setup.sh
```

### Run the Application

```
# Activate your venv if not already active
cd app
python main.py
```

### Notes

- Ensure `.env` is present before launching; otherwise the app will raise an error on startup.
- If you change schema or seed data, re-run `docs/database_creation.txt` against your database.
- Sample admin/trainer credentials are provided in the seed data (see `docs/database_creation.txt`).
- See `report.pdf` for additional information.
