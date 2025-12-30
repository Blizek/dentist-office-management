# Dentman — Dentist Office Management

Dentman is a Django-based system for managing a dental office: patients, staff, contracts, schedules, and content. It ships with a modern setup (uv, Docker, Nginx, GitHub Actions) and a clean modular structure.

**Highlights**
- **Django 5**: Custom `User`, models for ops/man modules, forms, signals
- **uv**: Fast, reproducible dependency and Python manager
- **Docker**: App + Nginx + Postgres compose for local/dev
- **Static/Media**: Configured static/media/storage directories
- **Tests**: `pytest` with Django, in-memory file storage in tests
- **CI**: GitHub Actions runs tests on push/PR

**Repo Structure (key paths)**
- App entry and config: [manage.py](manage.py), [dentman/settings/__init__.py](dentman/settings/__init__.py)
- Core apps: [dentman/app](dentman/app), [dentman/ops](dentman/ops), [dentman/man](dentman/man)
- Web server and containerization: [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), [etc/nginx](etc/nginx)
- Static/public roots: [pub](pub), [templates](templates)
- CI: [.github/workflows/tests.yml](.github/workflows/tests.yml)

---

**Quick Start (Local, SQLite + uv)**

Prerequisites:
- Python 3.12+
- uv (package manager)

1) Clone and enter the project directory
```bash
git clone https://github.com/Blizek/dentist-office-management.git
cd dentist-office-management/app
```

2) Create local env file (minimal dev defaults)
```bash
cp .env.local .env || true
printf "ENV=dev\nDEBUG=True\nSECRET_KEY=dev-secret-key\nDATABASE_URL=sqlite:///db.sqlite3\n" > .env
```

3) Install dependencies and set up the DB
```bash
brew install uv               # macOS: install uv
uv python install 3.12        # ensure Python 3.12 is available
uv sync                       # create .venv and install deps
uv run python manage.py migrate
uv run python manage.py createsuperuser
```
Linux (alternative):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv sync
```

4) Run the development server
```bash
uv run python manage.py runserver 0.0.0.0:8000
```

Open http://localhost:8000 and admin at http://localhost:8000/admin

---

**Quick Start (Docker, Postgres + Nginx)**

Prerequisites:
- Docker and Docker Compose

1) Prepare environment
Create a local config file from the sample:
```bash
cp .env.sample .env.local
# Set your .env.local variables
make env
```
This generates `.env` from `.env.local` variables using the Makefile. Adjust values as needed (domain, DB, ports).

2) Build images
```bash
make build
```

3) Start the stack (app + web + db)
```bash
make up
```

4) Apply migrations and create admin user
```bash
make migrate
make superuser
```

Useful targets:
- `make bash` — shell into app container
- `make web` — shell into nginx container
- `make down` — stop and remove containers
- `make upd` — run stack in detached mode

Nginx serves the app (proxy to Uvicorn) and public files from [pub](pub). Static and media roots are configured in settings.

---

**Configuration Basics**
- Settings module: [dentman/settings/__init__.py](dentman/settings/__init__.py) (dev overlay: [dentman/settings/dev.py](dentman/settings/dev.py))
- Key paths:
	- `STATIC_URL` → `s/`, `STATIC_ROOT` → `pub/s/`
	- `MEDIA_URL` → `m/`, `MEDIA_ROOT` → `pub/m/`
	- `STORAGE_URL` → `/storage/`, `STORAGE_ROOT` → `storage/`
- Database: `DATABASE_URL` via `django-environ` (defaults to SQLite)
- Custom user: `AUTH_USER_MODEL = "app.User"`

Minimal `.env` for local dev (SQLite):
```bash
ENV=dev
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

For a full example of environment variables used by Docker compose and the Makefile, see [.env.sample](.env.sample). Copy it to `.env.local` and adjust values as needed.

---

**Running Tests**
```bash
uv sync --group dev    # install dev dependencies (pytest, plugins)
uv run pytest
```
Notes:
- Test discovery and Django settings come from [pytest.ini](pytest.ini)
- File writes are redirected to memory during tests via fixtures in [conftest.py](conftest.py), so tests don’t litter the disk
- CI runs tests against Postgres; locally you can use SQLite (default) or export `DATABASE_URL` to point to Postgres.

---

**Continuous Integration**
- GitHub Actions workflow: [.github/workflows/tests.yml](.github/workflows/tests.yml)
- Triggers on push and PR, installs via uv, and runs `pytest`

Caching is enabled in CI; dependency sync uses `uv lock`/`uv sync` with the committed `uv.lock` file for reproducible installs.

---

**Makefile Shortcuts**
Useful developer commands defined in [Makefile](Makefile):
- `make env` — generate `.env` from `.env.local`
- `make build` — build project
- `make up` - run project
- `make upd` - run project in background
- `make migrate` / `make migrations` — database tasks
- `make superuser` - create project's superuser
- `make bash` / `make root` — shell into containers
- `make tests` — run tests inside container (pass `ARGS="filename.py"` to tests only from passed file)

Tip: The Dockerfile uses uv and the committed `uv.lock` for deterministic builds. Run `uv lock` when you change dependencies.

---

**License**
This project is licensed under the MIT License. See [LICENSE](LICENSE).
