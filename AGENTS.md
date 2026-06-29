# AGENTS.md

## Cursor Cloud specific instructions

This repository is a single Flask app (ParkingBooker — a parking reservation system, UI in Russian) backed by SQLite. There is no separate frontend build; pages are server-rendered Jinja2 templates.

### Services

| Service | Purpose | Run command (dev) | Port |
| --- | --- | --- | --- |
| Flask web app | Booking UI + admin panel + JSON debug routes | `.venv/bin/python main.py` | 5000 |

### Running

- Dependencies are managed with `uv` (`uv.lock` / `pyproject.toml`); the startup update script runs `uv sync`, which creates `.venv/`.
- Dev server: `.venv/bin/python main.py` (Flask dev server with `debug=True`, binds `0.0.0.0:5000`). This is the development entrypoint; do not use the gunicorn command from the `Dockerfile`/`docker-compose.yml` for local dev.
- The SQLite DB is auto-created at `instance/parking.db` on startup via `db.create_all()`, and default `ParkingSettings` are seeded. No manual migration step is needed — the `migrations/` folder has no versions and Alembic is not used at runtime.

### Non-obvious notes

- The booking form's date inputs are `datetime-local` (require both date AND time). Submitting with only a date and blank time triggers an HTML5 validation tooltip — fill the time portion too.
- Admin panel: `/admin/login`, default credentials `admin` / `admin123` (override with `ADMIN_PASSWORD`).
- Useful JSON debug routes (require admin login): `/debug/bookings`, `/debug/database`.
- No automated tests or lint configuration exist in this repo despite README mentions of `pytest`; the `tests/` directory does not exist.
- Optional env vars: `SESSION_SECRET`, `DATABASE_URL` (defaults to `sqlite:///parking.db`), `ADMIN_PASSWORD`. None are required to run locally.
