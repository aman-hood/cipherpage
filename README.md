# CipherPage Architecture & Monorepo Layout

Welcome to **CipherPage**, the enterprise-grade EdTech platform built on the vision of **Learn, Apply, Grow**.

## Monorepo Directory Structure

The following ASCII tree outlines our monorepo structure, ensuring strict separation of concerns across our FastAPI backend, Flutter mobile client, and Next.js web application.

```text
cipherpage/
├── backend/                  # Python FastAPI Application
│   ├── app/
│   │   ├── main.py           # Application Entrypoint
│   │   ├── core/             # Application Core (Config, Security, Logging)
│   │   ├── database/         # DB session, connection pooling
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic models (DTOs)
│   │   ├── repositories/     # Data access patterns
│   │   ├── services/         # Business logic
│   │   ├── routers/          # FastAPI Endpoints
│   │   ├── dependencies/     # Dependency injection
│   │   ├── workers/          # Celery background tasks
│   │   └── utils/            # Shared utilities
│   ├── tests/                # Pytest suites
│   ├── alembic.ini           # Alembic migrations config
│   ├── requirements.txt      # Dependencies
│   ├── Dockerfile
│   └── .env.example          # Environment variables template
├── mobile/                   # Flutter Application
│   ├── lib/
│   │   ├── core/             # Core utilities, theme, network, routing
│   │   ├── features/         # Feature modules (auth, home, courses, etc.)
│   │   └── main.dart
│   ├── pubspec.yaml          # Flutter dependencies
│   └── .env.example          # Environment variables template
├── web/                      # React Web Application (Next.js, TypeScript, Tailwind CSS)
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Shared React components
│   │   ├── features/         # Feature modules (auth, courses, learning, etc.)
│   │   ├── pages/            # Legacy or specific pages if needed
│   │   ├── layouts/          # Shared layouts
│   │   ├── services/         # API integration
│   │   ├── stores/           # Zustand state management
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Helper functions
│   ├── public/               # Static assets
│   ├── package.json          # NPM dependencies
│   └── .env.example          # Environment variables template
├── docker-compose.yml        # Local Dev Environment Orchestration
└── README.md                 # Project Overview (This file)
```

## Environment Variables Configuration

CipherPage relies on environment variables to configure its various services securely without hardcoding credentials into the source code. 

1. Navigate to the respective directories (`backend`, `web`, `mobile`).
2. Copy the provided `.env.example` file and rename it to `.env`.
   ```bash
   cp backend/.env.example backend/.env
   cp web/.env.example web/.env
   cp mobile/.env.example mobile/.env
   ```
3. Update the `.env` files with your local or production secrets. Note that `docker-compose.yml` automatically picks up `backend/.env` and `web/.env` using the `env_file` directive. Do not commit `.env` files to version control.

## Runtime services

- FastAPI uses SQLAlchemy with PostgreSQL on Neon for application data. Local and deployment configuration must provide the project owner's DATABASE_URL through backend/.env or a secret manager. TLS is required for remote PostgreSQL connections.
- Firebase Authentication manages user identities. Web and mobile clients use public Firebase project configuration; FastAPI verifies bearer ID tokens with Firebase Admin. Firebase Admin credentials belong only in the backend environment or a trusted runtime identity.
- Local Compose starts Redis, FastAPI, the worker, and Next.js; it does not create a PostgreSQL service. Set DATABASE_URL before starting the backend.
- Production web images need NEXT_PUBLIC_API_URL and the public NEXT_PUBLIC_FIREBASE_* values at build time. The production Compose file intentionally fails configuration when required Firebase web values are missing.

See docs/migrations/neon_firebase_migration.md for identity mapping, owner-provided variables, migration order, and remaining deployment prerequisites.
