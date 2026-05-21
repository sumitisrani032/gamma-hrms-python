# Gamma HRMS - Python Backend Module

This is the Python backend module for the GammaHRMS project, built with **FastAPI** and managed by **uv**.

## Project Structure

```text
gamma-python-backend/
├── alembic/                   # Alembic migration environment
│   ├── env.py
│   └── versions/              # Payroll migrations split by table/domain dependency
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Backward-compatible settings import
│   ├── core/                  # Application settings and shared core config
│   ├── db/                    # SQLAlchemy base/session wiring
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic
│   ├── repositories/          # Persistence/query layer
│   ├── payroll/               # Payroll domain package
│   └── api/
│       ├── __init__.py
│       ├── deps/              # FastAPI dependencies
│       └── v1/
│           ├── __init__.py
│           ├── api.py         # Main router aggregating all routes
│           └── endpoints/
│               ├── __init__.py
│               └── health.py  # Health-check endpoints
├── alembic.ini
├── .env.example               # Template for environment settings
├── pyproject.toml             # uv project & dependency configuration
└── README.md                  # This setup guide
```

---

## Setup Instructions (using uv)

[uv](https://github.com/astral-sh/uv) is a modern, fast Python package and project manager. Follow these steps to set up and run the FastAPI project locally:

### 1. Set Up Environment Variables

Copy the `.env.example` file to create your local `.env` configuration file:

```bash
# Navigate to the Python backend directory:
cd gamma-python-backend

# Copy env template
cp .env.example .env
```

You can open `.env` and adjust settings (such as `PORT`, `HOST`, or add database credentials) as needed.

For local database access, set:

```bash
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/gamma_hrms_development"
```

### 2. Synchronize / Install Dependencies

Install all dependencies and create the virtual environment automatically:

```bash
uv sync
```

This will automatically create a `.venv` directory and synchronize it with the dependencies specified in `pyproject.toml`.

### 3. Run the FastAPI Application

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

*Note: `uv run` will automatically run the command in the context of the project's virtual environment. You don't even need to activate the virtual environment manually.*

---

## Adding/Removing Dependencies

Since we are using `uv`'s project management features:

- **To add a dependency:**
  ```bash
  uv add package-name
  ```
- **To remove a dependency:**
  ```bash
  uv remove package-name
  ```
- **To add a development dependency:**
  ```bash
  uv add --dev pytest
  ```

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation for your endpoints. Once the server is running, visit:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Interactive testing UI)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (Clean, structured documentation UI)

## Key Endpoints

- **Root:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## Database Migrations

This module uses Alembic for Python-owned schema changes:

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
```

The salary/payroll schema has been split into ordered migration files under `alembic/versions`.

Important compatibility notes with the Ruby backend:

- Existing Ruby tables use UUID primary keys, so new payroll tables use UUIDs instead of bigint IDs.
- Existing Ruby tables are tenant-scoped with row-level security, so new payroll tables include `tenant_id` and enable the same `tenant_isolation_policy`.
- `employees`, `users`, `tenants`, `employee_bank_details`, and `audit_logs` already exist in the Ruby backend.
- The provided `employee_bank_accounts` table was not recreated. `payment_transactions.bank_detail_id` references the existing `employee_bank_details.id`.
- The provided `salary_audit_log` table was not recreated because the Ruby backend already owns the shared `audit_logs` table.
