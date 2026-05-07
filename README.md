# AI Roaster

AI Roaster is a small full-stack social app where a user can paste text, choose a roast style, and get back a scored roast with vibe tags, an aura label, and improvement tips.

The project is built as a portfolio-style app, so it has more than just a UI. There is a Django API, auth, post models, comments/reactions/bookmarks, moderation hooks, Celery tasks, WebSocket notification plumbing, Docker files, and a simple Windows startup script.

## What It Does

- Submit text or an image caption for roasting
- Pick categories like bio, outfit, setup, resume, dating profile, room, or portfolio
- Choose roast styles such as Brutal Roast, Gen Z Mode, Corporate Reviewer, and more
- Get a 5-6 line roast, score, aura, tags, and improvement tips
- Use a local demo login during development
- Test the backend API from Swagger docs
- Run everything locally with one script

## Tech Stack

Frontend:

- Next.js
- React
- Tailwind CSS
- Framer Motion
- lucide-react icons

Backend:

- Django
- Django REST Framework
- Simple JWT
- Celery
- Redis
- Django Channels
- PostgreSQL support
- SQLite fallback for local testing

AI/media:

- OpenAI-ready roast generation
- OpenAI moderation-ready safety check
- Cloudinary upload hook

## Folder Structure

```text
.
|-- backend/              Django API
|-- frontend/             Next.js frontend
|-- scripts/              Windows helper scripts
|-- docker-compose.yml    Full local stack with Postgres + Redis
|-- requirements.txt      Root pointer to backend requirements
`-- README.md
```

## Requirements

Install these first:

- Node.js 22 or newer
- Python 3.13 or newer
- Git

Optional:

- Docker Desktop, if you want to run Postgres and Redis through Docker

Python dependencies are listed in:

```text
backend/requirements.txt
```

There is also a root `requirements.txt` that points to the backend requirements file.

## Quick Start On Windows

From the project root, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Or just double-click:

```text
start-roastly.bat
```

The script will:

- create/use the backend virtual environment
- install Python dependencies
- install frontend dependencies
- run Django migrations
- start the backend on port `8000`
- start the frontend on port `3000`

Open the app:

```text
http://127.0.0.1:3000
```

Open API docs:

```text
http://127.0.0.1:8000/api/docs/
```

Stop the app:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

Or double-click:

```text
stop-roastly.bat
```

## Smoke Test

After starting the app, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-smoke.ps1
```

Or double-click:

```text
test-roastly.bat
```

The smoke test checks:

- frontend is reachable
- backend docs are reachable
- demo login works
- roast creation works
- roast output has at least 5 lines

## Manual Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:3000
```

## Manual Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/api/docs/
```

## Environment Variables

Copy the example file:

```powershell
copy .env.example .env
```

Most local testing works without an OpenAI key. If `OPENAI_API_KEY` is empty, the backend uses a mock roast response so the app still runs.

Useful variables:

```text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DATABASE_URL=
REDIS_URL=
OPENAI_API_KEY=
OPENAI_ROAST_MODEL=
OPENAI_MODERATION_MODEL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Docker Setup

If Docker Desktop is running:

```powershell
copy .env.example .env
docker compose up --build
```

Then apply migrations:

```powershell
docker compose exec backend python manage.py migrate
```

Create an admin user:

```powershell
docker compose exec backend python manage.py createsuperuser
```

Open:

```text
Frontend: http://localhost:3000
API docs: http://localhost:8000/api/docs/
Admin:    http://localhost:8000/admin/
```

## Deploying

Use Render for the Django backend and Vercel for the Next.js frontend.

The repo includes:

```text
render.yaml
DEPLOYMENT.md
```

Full deployment steps are in:

```text
DEPLOYMENT.md
```

## Useful API Routes

```text
POST   /api/v1/accounts/users/
POST   /api/v1/accounts/users/demo_token/
POST   /api/v1/auth/token/
GET    /api/v1/accounts/users/me/
POST   /api/v1/roasts/posts/
GET    /api/v1/roasts/posts/trending/
GET    /api/v1/roasts/posts/recent/
GET    /api/v1/roasts/posts/{id}/comments/
POST   /api/v1/roasts/posts/{id}/comments/
POST   /api/v1/roasts/posts/{id}/react/
POST   /api/v1/roasts/posts/{id}/bookmark/
GET    /api/v1/moderation/queue/
```

## Development Checks

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Backend:

```powershell
cd backend
.\.venv\Scripts\activate
python manage.py check
```

Smoke test from project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-smoke.ps1
```

## Notes

This is a development project, not a production moderation policy. The brutal roast mode is intentionally sharper, but the backend prompt still avoids hate speech, slurs, racist content, threats, and sexual harassment.

Before deploying publicly, use real environment secrets, managed Postgres/Redis, cloud storage for uploads, proper logging, and production-safe Django settings.
