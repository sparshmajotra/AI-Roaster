# Roastly

Roastly is a full-stack AI social platform where people submit images or text and receive playful AI roasts, scores, vibe tags, aura labels, improvement tips, and community feedback.

## Stack

- Frontend: Next.js 16, React 19, Tailwind CSS 4, Framer Motion, lucide-react
- Backend: Django 5.2, Django REST Framework, Simple JWT, Channels, Celery
- Data: PostgreSQL in Docker, SQLite fallback for quick local backend checks
- Async/realtime: Redis, Celery worker, Channels WebSocket notifications
- AI/media: OpenAI moderation + multimodal roast generation, Cloudinary upload hook
- Deployment: Docker Compose and GitHub Actions CI

## Project Structure

```text
frontend/   Next app with the polished Roastly product UI
backend/    Django API, social models, AI pipeline, moderation, notifications
```

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Then run migrations in the backend container:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

Open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Easiest Local Test On Windows

Double-click `start-roastly.bat`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Then open:

- Frontend: http://127.0.0.1:3000
- API docs: http://127.0.0.1:8000/api/docs/

To verify the local stack:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-smoke.ps1
```

To stop both dev servers, double-click `stop-roastly.bat`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

## Local Frontend Only

```bash
cd frontend
npm install
npm run dev
```

The UI includes a local interactive AI-result mock. Set `NEXT_PUBLIC_API_URL` when wiring it to the Django API.

## Local Backend Only

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If `OPENAI_API_KEY` is empty, the roast task uses a deterministic mock response so development does not block on external services.

## Key API Routes

- `POST /api/v1/accounts/users/` register
- `POST /api/v1/auth/token/` JWT login
- `GET /api/v1/accounts/users/me/` current profile
- `POST /api/v1/accounts/users/{id}/follow/`
- `GET /api/v1/roasts/posts/trending/`
- `POST /api/v1/roasts/posts/` create roast submission
- `GET|POST /api/v1/roasts/posts/{id}/comments/`
- `POST|DELETE /api/v1/roasts/posts/{id}/react/`
- `POST|DELETE /api/v1/roasts/posts/{id}/bookmark/`
- `GET /api/v1/moderation/queue/` admin review queue
- `WS /ws/notifications/{user_id}/?token=<jwt_access_token>`

## AI Safety

Submissions run through moderation before AI generation. The roast system prompt enforces playful, non-hateful humor and asks the model to return JSON:

```json
{
  "roast": "...",
  "rating": 7.6,
  "vibe_tags": ["..."],
  "aura": "...",
  "improvement_suggestions": ["..."]
}
```

## Production Notes

- Move secrets to your platform secret manager.
- Set `DJANGO_DEBUG=False`, strict `DJANGO_ALLOWED_HOSTS`, and production CORS origins.
- Use managed PostgreSQL, Redis, object storage, error tracking, and structured logs.
- Run Celery workers separately from the ASGI web process.
- Add CDN rules for uploaded media and generated share cards.
