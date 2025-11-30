## COMP 3005 – Database Management Systems Final Project

A console-based management system for a health and fitness club, built with Python and PostgreSQL using SQLAlchemy ORM.

Built by Afaq Virk and Raymond Liu

### Video Demo

Link to demo: https://youtu.be/VrSF7mgAM7Y

### Project Structure

- `app/`
  - `main.py`: Application entry, login/register routing based on role
  - `member.py`: Member workflows (dashboard, metrics, goals, sessions)
  - `trainer.py`: Trainer workflows and scheduling
  - `admin.py`: Admin workflows (rooms, equipment, billing)
  - `cli_utils.py`: Console UI helpers
  - `auth.py`: Handles connection to database
  - `seed.py`: Handles reseting/seeding database
- `models/`
  - `models.py`: SQLAlchemy ORM models (User, Role, Metric, Goal, Schedule, Session, Billing, etc.)
  - `__init__.py`: Model exports
- `docs/`

  - `database_creation.txt` original SQL schema/seed used for documentation (no longer used)
  - `ERD.pdf`: Entity-Relationship diagram
  - `report.pdf`: Project report

- Root
  - `env.template`: example environment variables (copy to `.env` and edit)
  - `requirements.txt`: python package requirements

### Prerequisites

- Python 3.10+
- PostgreSQL
- pip

### Environment Configuration

Use a `.env` file with PG\* variables (preferred). Copy `env.template` to `.env` and fill in:

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=Final_Project
PGUSER=postgres
PGPASSWORD=your_password
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

### Database Setup (Reset/Seed for Testing)

The application can reset the schema and seed sample data via the ORM:

```
python app/main.py --reset
```

This will:

- Drop and recreate all tables
- Insert roles, lookup tables, users, schedules/sessions, enrollments, services/bills/items, and sample metrics

If you prefer raw SQL, `docs/database_creation.txt` is provided for reference, but it is not required to run the app.

### Run the Application

```
# Activate your venv if not already active
cd app
python main.py
```

### Notes

- Ensure `.env` is present before launching; otherwise the app will raise an error on startup.
- Use `python app/main.py --reset` to rebuild and seed the database for tests.
- `docs/database_creation.txt` is optional and kept for documentation/deliverables.
- Sample admin/trainer credentials are provided in the seed data.
- See `report.pdf` for additional information.
