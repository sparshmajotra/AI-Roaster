# Deployment Guide

This repo is a monorepo:

```text
backend/   Django API
frontend/  Next.js app
```

The simplest deployment is:

- Backend on Render
- Frontend on Vercel

That keeps the Django API, database, and frontend separate and easier to debug.

## 1. Deploy The Backend On Render

The repo includes `render.yaml` at the root. Render calls this a Blueprint.

Steps:

1. Go to Render.
2. Click **New +**.
3. Choose **Blueprint**.
4. Connect this GitHub repo:

   ```text
   https://github.com/sparshmajotra/AI-Roaster
   ```

5. Render should detect `render.yaml`.
6. Apply the Blueprint.

It creates:

- `ai-roaster-api` web service
- `ai-roaster-db` PostgreSQL database

The backend service uses:

```text
buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
preDeployCommand: python manage.py migrate
startCommand: daphne -b 0.0.0.0 -p $PORT roastly.asgi:application
```

Render will ask for these optional secrets:

```text
OPENAI_API_KEY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

You can leave them empty for the first deploy. If `OPENAI_API_KEY` is empty, the backend uses the mock roast generator.

After deploy, your API should be available at something like:

```text
https://ai-roaster-api.onrender.com
```

Check:

```text
https://ai-roaster-api.onrender.com/health/
https://ai-roaster-api.onrender.com/api/docs/
```

## 2. Deploy The Frontend On Vercel

Steps:

1. Go to Vercel.
2. Click **Add New Project**.
3. Import the same GitHub repo:

   ```text
   https://github.com/sparshmajotra/AI-Roaster
   ```

4. Set **Root Directory** to:

   ```text
   frontend
   ```

5. Framework should be detected as **Next.js**.
6. Add this environment variable:

   ```text
   NEXT_PUBLIC_API_URL=https://ai-roaster-api.onrender.com/api/v1
   ```

   If Render gives you a different backend URL, use that instead.

7. Deploy.

## 3. Connect Frontend URL Back To Backend

Once Vercel gives you a frontend URL, copy it. It will look like:

```text
https://your-project.vercel.app
```

In Render, open the `ai-roaster-api` service and update environment variables:

```text
CORS_ALLOWED_ORIGINS=https://your-project.vercel.app
ROASTLY_FRONTEND_URL=https://your-project.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app
```

The included Render config already allows Vercel preview URLs through:

```text
CORS_ALLOWED_ORIGIN_REGEXES=^https://.*\.vercel\.app$
```

Still, setting the exact production frontend URL is cleaner.

Redeploy the backend after changing environment variables.

## 4. Test Production

Open the Vercel frontend and press **Roast me**.

You can also test the backend directly:

```powershell
$demo = Invoke-RestMethod -Method Post -Uri https://ai-roaster-api.onrender.com/api/v1/accounts/users/demo_token/
$headers = @{ Authorization = "Bearer $($demo.access)" }
$body = @{
  category = "Roast My Bio"
  roast_style = "Brutal Roast"
  visibility = "public"
  text_content = "Testing production deploy."
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri https://ai-roaster-api.onrender.com/api/v1/roasts/posts/ -Headers $headers -ContentType "application/json" -Body $body
```

## Notes

- Render free services may sleep when unused, so the first request can be slow.
- The current Render config runs Celery tasks inline with `CELERY_TASK_ALWAYS_EAGER=True`. That keeps the first deploy simple.
- For a more production-like setup, add a Render Key Value instance and a paid background worker for Celery.
- Add `OPENAI_API_KEY` when you want real AI output instead of the mock generator.
