# Deployment Guide

This repo is a monorepo:

```text
backend/   Django API
frontend/  Next.js app
```

The simplest free deployment is now:

- Backend on Render
- Frontend on Render Static Sites

That keeps the Django API, database, and frontend separate while avoiding Vercel monorepo detection issues.

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

- `ai-roaster-frontend` static site
- `ai-roaster-api` web service
- `ai-roaster-db` PostgreSQL database

The backend service uses:

```text
buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
startCommand: python manage.py migrate && daphne -b 0.0.0.0 -p $PORT roastly.asgi:application
```

Render's free tier does not support `preDeployCommand`, so migrations run at service startup.

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

## 2. Deploy The Frontend On Render

If you used the Blueprint, Render should create the frontend static site automatically.

If you create it manually:

1. Go to Render.
2. Click **New +**.
3. Choose **Static Site**.
4. Connect this GitHub repo:

   ```text
   https://github.com/sparshmajotra/AI-Roaster
   ```

5. Set **Root Directory** to:

   ```text
   frontend
   ```

6. Set **Build Command** to:

   ```text
   npm install && npm run build
   ```

7. Set **Publish Directory** to:

   ```text
   out
   ```

8. Add this environment variable:

   ```text
   NEXT_PUBLIC_API_URL=https://ai-roaster-api.onrender.com/api/v1
   ```

   If Render gives you a different backend URL, use that instead.

9. Deploy.

## 3. Connect Frontend URL Back To Backend

Once Render gives you a frontend URL, copy it. It will look like:

```text
https://ai-roaster-frontend.onrender.com
```

In Render, open the `ai-roaster-api` service and update environment variables:

```text
CORS_ALLOWED_ORIGINS=https://ai-roaster-frontend.onrender.com
ROASTLY_FRONTEND_URL=https://ai-roaster-frontend.onrender.com
CSRF_TRUSTED_ORIGINS=https://ai-roaster-frontend.onrender.com
```

The included Render config already allows Render and Vercel preview URLs through:

```text
CORS_ALLOWED_ORIGIN_REGEXES=^https://.*\.vercel\.app$,^https://.*\.onrender\.com$
```

Still, setting the exact production frontend URL is cleaner.

Redeploy the backend after changing environment variables.

## 4. Test Production

Open the Render frontend and press **Roast me**.

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
