# Deployment

## Deploy now: the portfolio dashboard

This repository includes a Render Blueprint in `render.yaml`. It builds a public, static dashboard from `dashboard.html` and publishes only the generated `dist/` folder.

The build deliberately replaces local campaign data with synthetic `demo.invalid` contacts. It does not publish `.env`, SQLite data, Gmail credentials, OpenAI keys, or real prospect data.

1. Push this repository to GitHub.
2. In Render, select **New → Blueprint** and connect the repository.
3. Render detects `render.yaml`. Create the `outreach-agent-portfolio` static site.
4. Use the generated `onrender.com` URL in your CV and interviews.

To test the exact public build locally:

```powershell
python scripts/build_demo_site.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`.

## Do not deploy yet: the sender

The Python outreach workflow currently uses a local SQLite database and SMTP credentials. Keep it local while you demonstrate the portfolio dashboard.

For production delivery, first add a FastAPI API, migrate SQLite to PostgreSQL, and store credentials in Render environment variables. Then deploy three private services: a Python API, PostgreSQL, and a scheduled worker for follow-ups. Never put API keys or email credentials in the static site.
