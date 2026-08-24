# CipherPage Architecture & Monorepo Layout

Welcome to **CipherPage**, the enterprise-grade EdTech platform built on the vision of **LAG: Learn, Apply, Grow**.

## Monorepo Directory Structure

The following ASCII tree outlines our monorepo structure, ensuring strict separation of concerns (Presentation, Domain, Data layers) across our FastAPI backend, Flutter mobile client, and React web application.

```text
cipherpage/
├── backend/                  # Python FastAPI Application
│   ├── app/
│   │   ├── api/              # Presentation Layer (FastAPI Routers, Endpoints)
│   │   │   ├── v1/
│   │   │   └── dependencies.py
│   │   ├── core/             # Application Core (Config, Security, Celery config)
│   │   ├── domain/           # Domain Layer (Business Logic, Pydantic schemas, Interfaces)
│   │   │   ├── schemas/      # Pydantic models (DTOs)
│   │   │   └── services/     # Business logic and use cases
│   │   ├── infrastructure/   # Data Layer (SQLAlchemy Models, Repositories, External APIs)
│   │   │   ├── database/     # DB session, connection pooling, Alembic migrations
│   │   │   ├── models.py     # SQLAlchemy ORM models (Database schema)
│   │   │   └── repositories/ # Data access patterns (CRUD operations)
│   │   ├── worker/           # Celery tasks (Background jobs, grading submissions)
│   │   └── main.py           # Application Entrypoint
│   ├── tests/                # Pytest suites
│   ├── pyproject.toml        # Poetry/pip dependencies
│   └── Dockerfile
├── mobile/                   # Flutter Application (Impeller, BLoC/Riverpod)
│   ├── lib/
│   │   ├── core/             # Core utilities, theme, network client, routing
│   │   ├── data/             # Data Layer (Repositories, API Data Sources, DTOs)
│   │   ├── domain/           # Domain Layer (Entities, Use Cases/Interactors, Repository Interfaces)
│   │   ├── presentation/     # Presentation Layer (Widgets, Screens, BLoC/Riverpod state)
│   │   │   ├── learn/        # Learn track UI
│   │   │   ├── apply/        # Apply track UI (Coding interface)
│   │   │   └── grow/         # Grow track UI (Portfolios)
│   │   └── main.dart
│   ├── pubspec.yaml          # Flutter dependencies
│   └── test/                 # Unit and Widget tests
├── web/                      # React Web Application (TypeScript, Tailwind CSS, Vite)
│   ├── src/
│   │   ├── assets/           # Static assets, icons, images
│   │   ├── core/             # Core configuration, Axios client, context providers
│   │   ├── data/             # Data Layer (API hooks, DTOs, React Query)
│   │   ├── domain/           # Domain Layer (TypeScript types, Interfaces, Business logic)
│   │   ├── presentation/     # Presentation Layer (React Components, Pages)
│   │   │   ├── admin/        # Admin Panel UI
│   │   │   └── student/      # Student Web App UI
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json          # NPM dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── tailwind.config.js    # Tailwind CSS styling configuration
├── docker-compose.yml        # Local Dev Environment Orchestration
└── README.md                 # Project Overview (This file)
```
