# SHADOW Web V1

**SHADOW — Private. Secure. Connected.**

A GitHub-ready Website V1 foundation for a private messaging platform.

## Included

- FastAPI backend
- PostgreSQL
- User registration and login
- Argon2id password hashing through `pwdlib`
- Short-lived JWT access tokens
- Rotating HttpOnly refresh-token sessions
- Logout and logout-all
- Basic account/profile endpoint
- Responsive SHADOW web UI
- Docker + Docker Compose
- Basic security headers

## 1. Quick start with Docker

Copy the environment file:

```bash
cp .env.example .env
```

Generate a strong secret for production. For example, with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the result into `.env` as `SECRET_KEY`.

Start the application:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

Stop:

```bash
docker compose down
```

## 2. GitHub

```bash
git init
git add .
git commit -m "Initial SHADOW Web V1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shadow-web-v1.git
git push -u origin main
```

Never commit `.env`.

## 3. API endpoints

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `GET /users/me`

FastAPI docs:

```text
http://localhost:8000/docs
```

## 4. Local Python development

You need PostgreSQL running and `DATABASE_URL` configured.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Linux/macOS:
```bash
source .venv/bin/activate
```

Windows:
```powershell
.venv\Scripts\activate
```

Install:

```bash
pip install -r backend/requirements.txt
```

Run from the project root:

```bash
uvicorn backend.app.main:app --reload
```

## Important security notes

This is V1, not a production security audit.

- Use HTTPS in production.
- Set `COOKIE_SECURE=true` in production.
- Use a strong random `SECRET_KEY`.
- Do not log passwords, refresh tokens, access tokens, or message plaintext.
- Use database migrations (Alembic) before production instead of startup `create_all`.
- Add rate limiting and login abuse protection before public deployment.
- E2EE is not implemented in V1 yet. Do not call V1 end-to-end encrypted.
- Before claiming strong security, perform a threat model and independent security review.

## Roadmap

V1 → accounts, authentication, profiles

V1.5 → user search, conversations, WebSockets

V2 → established E2EE protocol design, device keys, verification, key rotation

V3 → encrypted media

V4 → groups, notifications, advanced privacy

V5 → voice/video calls and multi-device improvements
