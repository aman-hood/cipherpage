# CipherPage Initial Discovery Baseline

**Captured:** 2026-10-18  
**Repository state:** branch `main`, commit `3f15111`, 303 tracked files, working tree clean before this report was added.

## Scope and handling

This is an architecture and execution baseline, not a correctness or security audit. All tracked paths were inventoried. Manifests, deployment and infrastructure definitions, migrations, tests, runbooks, application entrypoints, route maps, service boundaries, auth, AI/RAG and code-execution integrations were inspected to establish the system map. The checklist below is the file-by-file review queue for the subsequent audit.

Local ignored environment files exist in backend, web and mobile. Their values were not read into this report. Only variable names and presence were checked. No application code, dependency manifests, schemas, infrastructure definitions or environment settings were changed. The report itself is the only intended repository addition; build/cache outputs are ignored.

## 1. Architecture and technology stack

| Area | Verified implementation |
| --- | --- |
| Web application | Next.js 16.3.5 App Router, React 19.2.8, TypeScript 5, Tailwind CSS 4, ESLint 9, Supabase SSR/JS, Monaco Editor and ReactPlayer. Static pages, browser storage and service wrappers coexist. The Next build is configured for standalone output. |
| Backend/API | Python 3.11 container target; local virtual environment uses Python 3.12.8. FastAPI 0.110, Pydantic 2, SQLAlchemy 2, Alembic, psycopg2, pgvector, PyJWT/passlib, Celery/Redis, Prometheus client and REST endpoints under `/api/v1`. |
| Database | PostgreSQL 15 with SQLAlchemy models and Alembic migrations. The document embedding column uses pgvector's 384-dimensional vector type when available, with JSON as an import fallback. Local and Terraform definitions use pgvector-capable PostgreSQL. |
| Background work/cache | Celery worker and Redis broker/result backend. The code-submission service queues a Celery grading task and attempts synchronous evaluation if dispatch fails. |
| Authentication | Supabase Auth is the identity provider in web and Flutter. The backend validates Supabase HS256 JWTs using `SUPABASE_JWT_SECRET`, synchronizes users into its own database, and checks STUDENT/TEACHER/ADMIN roles. A demo token is accepted only when development mode and the explicit dev-token setting are both enabled. The backend exposes `/auth/me`, not login or registration endpoints. |
| AI and RAG | A custom adapter tries Google Gemini, then OpenAI, then a built-in local pedagogical response. Embeddings try Gemini and otherwise use a deterministic hashed word/subword vector. Chunks and embeddings are stored in PostgreSQL and retrieved with pgvector cosine distance when available plus lexical filtering. No separate vector database or RAG framework is declared. |
| Code execution | Python submissions are statically checked and run in a disposable Docker container when Docker is available; otherwise the runner falls back to a sanitized local subprocess. Celery processes submissions and updates submission and gamification records. |
| Payments | Backend payment routes contain an optional direct Stripe PaymentIntent request, a development simulation, and a webhook route. The webhook implementation is a partial signature-check skeleton. No web payment service or UI integration was found in the inspected frontend service map. |
| Mobile | Flutter / Dart client with Supabase login and registration, a basic authenticated home screen, and a Dio request to synchronize the session with FastAPI. The manifest also declares flutter_bloc, shared_preferences and video_player. Current screens do not implement course, practice, AI or progress flows. |
| Deployment and observability | Docker Compose, multi-stage Dockerfiles, Jenkins pipelines, Terraform AWS definitions, a partial CloudFormation stack, one standalone Lambda handler, and Prometheus/Grafana configuration. |

### Repository modules

- `backend/`: FastAPI application, ORM and schemas, repositories/services/routers, integrations, Celery tasks, Alembic and unittest suites.
- `web/`: Next.js application, Supabase auth helpers, REST service wrappers, UI components and local sample data.
- `mobile/`: Flutter client plus Android, iOS, Linux, macOS, web and Windows platform shells.
- `infra/`: Terraform, CloudFormation and an unconnected serverless media handler.
- `deploy/`: Jenkins controller, monitoring Compose stack and a second Jenkins pipeline copy.
- `monitoring/`: Prometheus scrape/alert config and Grafana provisioning/dashboard.
- `scripts/`: PowerShell and Bash pipeline/IaC validation scripts.
- `docs/runbooks/`: CI/CD, AWS deployment, observability and backup/recovery procedures.

There is no root-level JavaScript monorepo manifest, no tracked `.github/workflows` directory, and no separate frontend or mobile backend. CI is Jenkins-based.

## 2. API, persistence and primary data flows

### API surface

The FastAPI application registers these route groups under `/api/v1`:

- Authentication: `GET /auth/me`.
- Learning content: courses list/detail/create/update/modules; lecture detail; enrollments create/list.
- Practice: challenges list/detail/create; submissions create/status/result/history.
- Learner state: progress summary/lecture update; stats, badges and certificates; notifications.
- Administration: user listing.
- AI: mentor request/quota, learning-assistant query, teacher document ingestion and document listing.
- Payments: create, verify and webhook.
- Operational endpoints: `GET /health` and `GET /metrics`.

Authorization is not uniform by route group: current-user dependencies protect selected routes; teacher/admin dependencies are used for selected write/admin routes; several catalog reads are public. Route-by-route authorization is a primary audit item.

### Data flow

1. A user signs in through Supabase in the web or mobile client. The client sends the Supabase access token to FastAPI. FastAPI decodes and validates it, then finds or inserts the local user row.
2. Web practice UI calls backend wrappers for challenge lookup and code submission. The backend persists a submission, dispatches a Celery task, retrieves test cases, calls the code runner, stores result rows and awards XP/badges on a first successful solve.
3. Web AI and RAG components call backend endpoints. Mentor requests check a daily database quota and persist usage. RAG ingestion currently accepts text content in the request, chunks and embeds it, and saves document/chunk rows. Questions are enrollment/role filtered, retrieved from PostgreSQL, then sent to the LLM adapter; citations are returned. The ingestion service uses an in-memory placeholder file path; no app-level S3 document persistence path was found.
4. Course/video completion, selected dashboard identity and solved-video state are also stored in browser localStorage. Course pages and dashboard sample content are not generally sourced through a course API wrapper.
5. The web YouTube route reads the bundled `youtubeData.ts` dataset. It does not call YouTube's external API.
6. Flutter initializes Supabase and calls only `GET /api/v1/auth/me` after auth changes. The URL is hard-coded for the Android emulator instead of using the supplied `API_BASE_URL` variable.

## 3. Deployment and operations

- Development Compose declares PostgreSQL/pgvector, Redis, FastAPI, Celery and Next.js.
- Production Compose declares the same five services and builds the backend/frontend production targets.
- The backend Dockerfile uses Python 3.11 and development/production targets. The web Dockerfile uses Node 22 and a Next standalone runner.
- The root Jenkinsfile and `deploy/jenkins/Jenkinsfile` both contain a Jenkins pipeline. The CI flow includes Python compilation, web lint/typecheck/audit, unittest discovery, Docker builds, Trivy scanning and a health smoke check. The local verification scripts invoke tests/builds and the infrastructure script invokes `terraform init`; those scripts were not run because they can mutate state or install/download dependencies.
- Terraform declares a VPC, ALB, S3 course assets, IAM roles, CloudWatch groups, ECS backend and frontend services, RDS PostgreSQL/pgvector and a budget. Although private subnets are declared, the inspected ECS services are attached to public subnets and receive public IPs. A Redis resource and Celery ECS service are not declared; there is a Celery log group only.
- The Terraform backend task definition does not set the required `JWT_SECRET` from backend settings, and does not wire Supabase JWT settings, Redis or Celery broker values. This is a deployment-readiness mismatch to resolve during the infrastructure audit.
- CloudFormation is a smaller scaffold: VPC/network, security groups, S3, ECS cluster and ALB. It does not declare the application task/service definitions, RDS or Redis present in the Terraform/Compose story.
- The Lambda handler validates S3-upload/API Gateway media metadata, but no Terraform or CloudFormation Lambda/API trigger wiring was found.
- Prometheus scrapes the backend `:8000/metrics`; Grafana is provisioned with a datasource and dashboard. The monitoring Compose file expects the application network to exist.
- Compose and Terraform contain credential fallback/default settings. Their values are intentionally omitted here and should be replaced with managed secrets before any production use.

## 4. Baseline commands and results

Commands were run using already-present tools and packages. No package install, upgrade, service startup, migration, Docker build or application-provider API call was initiated. The Next build did attempt its framework-managed Google Fonts download, which failed as recorded below.

| Command | Result |
| --- | --- |
| Backend Python compileall using `backend/venv/Scripts/python.exe -m compileall -q app` from `backend/` | **Passed.** |
| `npm run lint` from `web/` | **Failed:** 11 errors and 48 warnings. Errors include an unescaped apostrophe in the login page, React hook lint errors for synchronous state changes in effects, and a use-before-declaration finding in `useAuth.ts`. Warnings are mainly unused imports/variables and hook dependencies. |
| `web/node_modules/.bin/tsc.cmd --noEmit` from `web/` | **Passed.** |
| `npm run build` from `web/` | **Failed:** Next/Turbopack could not fetch Geist and Geist Mono from Google Fonts. This is a network dependency failure; the build did not complete. |
| `flutter.bat test --no-pub --reporter expanded` from `mobile/` | **Inconclusive:** no output or exit result after roughly two minutes; the process was interrupted. `--no-pub` prevented dependency installation. The sole tracked widget test is still the default counter smoke test, which does not match the current auth-based app. |
| `terraform fmt -check` from `infra/terraform/` | **Passed.** |
| `terraform validate` from `infra/terraform/` without running init | **Failed:** the local AWS provider plugin did not respond to the schema request. No provider initialization/download was attempted. |
| `docker compose -f docker-compose.yml config --quiet` | **Passed**, with an obsolete Compose `version` attribute warning. |
| `docker compose -f docker-compose.prod.yml config --quiet` | **Passed**, with the obsolete `version` warning and warnings that five Supabase substitutions were unset and defaulted blank. |
| Jenkins and monitoring Compose `config --quiet` checks | **Passed**, each with an obsolete `version` warning. |
| `docker info --format '{{.ServerVersion}}'` | **Unavailable:** Docker Desktop Linux engine pipe was absent; daemon is not running. |
| Local port probes for PostgreSQL 5432, Redis 6379, API 8000, web 3000 and Supabase 54321 | **Unavailable:** none were listening. |

### Tests intentionally not run

There are six backend unittest files and 29 test methods. They are not isolated unit-only tests: they open the configured database, expect seed records and/or a live API on port 8000; the hardening setup deletes AI usage rows, while the workflow tests create submissions and AI records. Running them against an unknown local database would mutate learner data. They need an isolated disposable database and service stack before execution. The backend virtual environment also has no pytest module, and the repository's declared runner is unittest rather than pytest.

The web package defines build, start, dev and lint scripts but no test script. No web unit/e2e test framework is declared. The mobile suite has one stale template counter widget test.

## 5. Prerequisites and configuration limitations

- Docker daemon is stopped; local PostgreSQL, Redis, FastAPI, Next and local Supabase ports are not listening. Full-stack and endpoint/integration suites cannot be baseline-verified here.
- Google Fonts network access is blocked/unavailable to the Next build. Build output could not establish whether a font-independent production bundle succeeds.
- Gemini, OpenAI, Stripe and YouTube API key environment variables are unset in the current process. The local backend env file also does not list provider-key names. The backend has local fallbacks for mentor responses/embeddings; live provider behavior is unverified. Stripe's paid flow and webhook are not live-verified.
- Supabase-related variables exist by name in the local ignored env files, but no Supabase endpoint was probed and the local Supabase port is not listening; external Supabase connectivity remains unverified.
- The tracked web `.env.example` contains only the API base URL, while web code also requires Supabase URL and anon key. Local web `.env` contains the relevant key names, but its values are private and were not inspected.
- The production Compose parse reports unset Supabase URL/anon/JWT substitutions. Populate these through the intended runtime secret mechanism before using that file.
- The Flutter sample declares `API_BASE_URL`, while the auth service hard-codes the Android emulator URL. The runtime ignores the sample API URL.
- Terraform validation requires a working local provider plugin. Running the documented `terraform init` would download provider dependencies, so it was not run under the no-install restriction.
- The backend test suite requires an isolated seeded database and a live backend/Redis/worker setup. Its direct localhost calls and mutating fixtures make it unsafe to run against the current unknown state.
- Documentation claims differ: CI comments/runbook refer to 21 tests in one location, while the backup runbook claims 29; current test source contains 29 methods.

## 6. Generated, vendored, build and binary files

These do not need manual line-by-line source review:

- Ignored local dependency/build/runtime trees: `web/node_modules/`, `web/.next/`, `backend/venv/`, Python `__pycache__/`, `mobile/.dart_tool/`, `mobile/build/`, and Terraform `.terraform/`. These are not tracked source; no tracked vendor directory was found.
- Generated Flutter registrants: `mobile/linux/flutter/generated_plugin_registrant.cc`, `mobile/linux/flutter/generated_plugin_registrant.h`, `mobile/linux/flutter/generated_plugins.cmake`, equivalent Windows files, and `mobile/macos/Flutter/GeneratedPluginRegistrant.swift`. Review only if validating plugin/platform registration.
- Flutter platform runner shells, project workspaces/schemes, and boilerplate build files are framework scaffolding. Review the platform-specific manifests/build settings for platforms that are actually shipped.
- Lockfiles are machine-generated dependency resolution records; review lockfile diffs and provenance, not each resolved package line.
- Binary images/icons: web logo and favicon; mobile logo; Android launcher mipmaps; iOS/macOS app icons and launch images; Flutter web icons/favicon; Windows app icon. Validate presence, dimensions and branding as needed, not line-by-line.
- Static SVGs and Grafana dashboard JSON are text assets. They are not runtime code, but review their content when auditing presentation/monitoring.

## 7. File-by-file review checklist

Use this checklist in subsequent audit phases. Generated files and binary assets are called out separately above.

### Root

- [ ] `.gitignore`
- [ ] `README.md`
- [ ] `docker-compose.yml`
- [ ] `docker-compose.prod.yml`
- [ ] `Jenkinsfile`

### Backend: packaging, configuration and migrations

- [ ] `backend/requirements.txt`
- [ ] `backend/.env.example`
- [ ] `backend/.dockerignore`
- [ ] `backend/Dockerfile`
- [ ] `backend/alembic.ini`
- [ ] `backend/alembic/README`
- [ ] `backend/alembic/env.py`
- [ ] `backend/alembic/script.py.mako`
- [ ] `backend/alembic/versions/10278e7e16ef_initial_schema.py`
- [ ] `backend/alembic/versions/44d1daf4ba49_add_phase_1_core_models.py`
- [ ] `backend/alembic/versions/fe013bbf584e_supabase_auth.py`
- [ ] `backend/alembic/versions/0d4b3d2be169_add_document_chunks_rag.py`

### Backend: runtime, core, persistence and auth

- [ ] `backend/app/main.py`
- [ ] `backend/app/core/config.py`
- [ ] `backend/app/core/exceptions.py`
- [ ] `backend/app/core/logging.py`
- [ ] `backend/app/core/metrics.py`
- [ ] `backend/app/core/rate_limiter.py`
- [ ] `backend/app/core/security.py`
- [ ] `backend/app/core/security_headers.py`
- [ ] `backend/app/database/base.py`
- [ ] `backend/app/database/session.py`
- [ ] `backend/app/database/seed.py`
- [ ] `backend/app/dependencies/auth.py`

### Backend: models and schemas

- [ ] `backend/app/models/__init__.py`
- [ ] `backend/app/models/user.py`
- [ ] `backend/app/models/course.py`
- [ ] `backend/app/models/enrollment.py`
- [ ] `backend/app/models/challenge.py`
- [ ] `backend/app/models/submission.py`
- [ ] `backend/app/models/progress.py`
- [ ] `backend/app/models/gamification.py`
- [ ] `backend/app/models/ai.py`
- [ ] `backend/app/schemas/auth.py`
- [ ] `backend/app/schemas/course.py`
- [ ] `backend/app/schemas/enrollment.py`
- [ ] `backend/app/schemas/challenge.py`
- [ ] `backend/app/schemas/submission.py`
- [ ] `backend/app/schemas/progress.py`
- [ ] `backend/app/schemas/gamification.py`
- [ ] `backend/app/schemas/payment.py`
- [ ] `backend/app/schemas/ai.py`
- [ ] `backend/app/schemas/rag.py`

### Backend: repositories and services

- [ ] `backend/app/repositories/base.py`
- [ ] `backend/app/repositories/user.py`
- [ ] `backend/app/repositories/course.py`
- [ ] `backend/app/repositories/enrollment.py`
- [ ] `backend/app/repositories/challenge.py`
- [ ] `backend/app/repositories/submission.py`
- [ ] `backend/app/repositories/progress.py`
- [ ] `backend/app/services/auth.py`
- [ ] `backend/app/services/course.py`
- [ ] `backend/app/services/enrollment.py`
- [ ] `backend/app/services/challenge.py`
- [ ] `backend/app/services/submission.py`
- [ ] `backend/app/services/progress.py`
- [ ] `backend/app/services/ai_mentor.py`
- [ ] `backend/app/services/rag_assistant.py`

### Backend: routers, workers and integrations

- [ ] `backend/app/routers/auth.py`
- [ ] `backend/app/routers/courses.py`
- [ ] `backend/app/routers/lectures.py`
- [ ] `backend/app/routers/enrollments.py`
- [ ] `backend/app/routers/payments.py`
- [ ] `backend/app/routers/submissions.py`
- [ ] `backend/app/routers/progress.py`
- [ ] `backend/app/routers/challenges.py`
- [ ] `backend/app/routers/gamification.py`
- [ ] `backend/app/routers/notifications.py`
- [ ] `backend/app/routers/admin.py`
- [ ] `backend/app/routers/ai.py`
- [ ] `backend/app/workers/__init__.py`
- [ ] `backend/app/workers/celery_app.py`
- [ ] `backend/app/workers/tasks.py`
- [ ] `backend/app/integrations/code_runner/__init__.py`
- [ ] `backend/app/integrations/code_runner/runner.py`
- [ ] `backend/app/integrations/llm/__init__.py`
- [ ] `backend/app/integrations/llm/adapter.py`
- [ ] `backend/app/integrations/vector_search/__init__.py`
- [ ] `backend/app/integrations/vector_search/chunker.py`
- [ ] `backend/app/integrations/vector_search/embeddings.py`
- [ ] `backend/app/integrations/vector_search/store.py`

### Backend: tests

- [ ] `backend/tests/test_phase1.py`
- [ ] `backend/tests/test_phase2_runner.py`
- [ ] `backend/tests/test_phase3_ai_mentor.py`
- [ ] `backend/tests/test_phase4_rag.py`
- [ ] `backend/tests/test_phase7_observability.py`
- [ ] `backend/tests/test_phase8_hardening.py`

### Web: manifests and configuration

- [ ] `web/package.json`
- [ ] `web/package-lock.json`
- [ ] `web/.env.example`
- [ ] `web/.dockerignore`
- [ ] `web/.gitignore`
- [ ] `web/AGENTS.md`
- [ ] `web/CLAUDE.md`
- [ ] `web/README.md`
- [ ] `web/Dockerfile`
- [ ] `web/eslint.config.mjs`
- [ ] `web/next.config.ts`
- [ ] `web/postcss.config.mjs`
- [ ] `web/tsconfig.json`

### Web: routes and pages

- [ ] `web/src/app/page.tsx`
- [ ] `web/src/app/layout.tsx`
- [ ] `web/src/app/globals.css`
- [ ] `web/src/app/(auth)/login/page.tsx`
- [ ] `web/src/app/(auth)/register/page.tsx`
- [ ] `web/src/app/auth/callback/route.ts`
- [ ] `web/src/app/api/youtube/route.ts`
- [ ] `web/src/app/dashboard/layout.tsx`
- [ ] `web/src/app/dashboard/page.tsx`
- [ ] `web/src/app/dashboard/courses/page.tsx`
- [ ] `web/src/app/dashboard/practice/page.tsx`
- [ ] `web/src/app/dashboard/achievements/page.tsx`

### Web: components, auth, data and services

- [ ] `web/src/components/AIMentorDrawer.tsx`
- [ ] `web/src/components/CourseRAGAssistant.tsx`
- [ ] `web/src/components/MonacoCodeEditor.tsx`
- [ ] `web/src/components/PracticeWorkspace.tsx`
- [ ] `web/src/components/VideoPlayer.tsx`
- [ ] `web/src/features/auth/hooks/useAuth.ts`
- [ ] `web/src/lib/supabase/client.ts`
- [ ] `web/src/lib/supabase/server.ts`
- [ ] `web/src/lib/supabase/middleware.ts`
- [ ] `web/src/lib/gamificationData.ts`
- [ ] `web/src/lib/problemsData.ts`
- [ ] `web/src/lib/youtubeData.ts`
- [ ] `web/src/middleware.ts`
- [ ] `web/src/services/aiMentorService.ts`
- [ ] `web/src/services/challengeService.ts`
- [ ] `web/src/services/gamificationService.ts`
- [ ] `web/src/services/ragService.ts`
- [ ] `web/src/services/submissionService.ts`

### Web: text-based static assets

- [ ] `web/public/file.svg`
- [ ] `web/public/globe.svg`
- [ ] `web/public/next.svg`
- [ ] `web/public/vercel.svg`
- [ ] `web/public/window.svg`

### Mobile: Flutter app and package

- [ ] `mobile/.gitignore`
- [ ] `mobile/pubspec.yaml`
- [ ] `mobile/pubspec.lock`
- [ ] `mobile/analysis_options.yaml`
- [ ] `mobile/.env.example`
- [ ] `mobile/README.md`
- [ ] `mobile/.metadata`
- [ ] `mobile/lib/main.dart`
- [ ] `mobile/lib/core/auth_wrapper.dart`
- [ ] `mobile/lib/features/auth/auth_service.dart`
- [ ] `mobile/lib/features/auth/login_screen.dart`
- [ ] `mobile/lib/features/auth/register_screen.dart`
- [ ] `mobile/lib/features/home/home_screen.dart`
- [ ] `mobile/test/widget_test.dart`

### Mobile: platform configuration and native integration

- [ ] `mobile/android/.gitignore`
- [ ] `mobile/android/app/build.gradle.kts`
- [ ] `mobile/android/app/src/debug/AndroidManifest.xml`
- [ ] `mobile/android/app/src/profile/AndroidManifest.xml`
- [ ] `mobile/android/app/src/main/AndroidManifest.xml`
- [ ] `mobile/android/app/src/main/kotlin/com/example/cipherpage_mobile/MainActivity.kt`
- [ ] `mobile/android/app/src/main/res/drawable/launch_background.xml`
- [ ] `mobile/android/app/src/main/res/drawable-v21/launch_background.xml`
- [ ] `mobile/android/app/src/main/res/values/styles.xml`
- [ ] `mobile/android/app/src/main/res/values-night/styles.xml`
- [ ] `mobile/android/build.gradle.kts`
- [ ] `mobile/android/gradle.properties`
- [ ] `mobile/android/gradle/wrapper/gradle-wrapper.properties`
- [ ] `mobile/android/settings.gradle.kts`
- [ ] `mobile/ios/.gitignore`
- [ ] `mobile/ios/Flutter/AppFrameworkInfo.plist`
- [ ] `mobile/ios/Flutter/Debug.xcconfig`
- [ ] `mobile/ios/Flutter/Release.xcconfig`
- [ ] `mobile/ios/Runner.xcodeproj/project.pbxproj`
- [ ] `mobile/ios/Runner.xcodeproj/project.xcworkspace/contents.xcworkspacedata`
- [ ] `mobile/ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- [ ] `mobile/ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings`
- [ ] `mobile/ios/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme`
- [ ] `mobile/ios/Runner.xcworkspace/contents.xcworkspacedata`
- [ ] `mobile/ios/Runner.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- [ ] `mobile/ios/Runner.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings`
- [ ] `mobile/ios/Runner/AppDelegate.swift`
- [ ] `mobile/ios/Runner/Info.plist`
- [ ] `mobile/ios/Runner/Runner-Bridging-Header.h`
- [ ] `mobile/ios/Runner/SceneDelegate.swift`
- [ ] `mobile/ios/Runner/Base.lproj/LaunchScreen.storyboard`
- [ ] `mobile/ios/Runner/Base.lproj/Main.storyboard`
- [ ] `mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json`
- [ ] `mobile/ios/Runner/Assets.xcassets/LaunchImage.imageset/Contents.json`
- [ ] `mobile/ios/Runner/Assets.xcassets/LaunchImage.imageset/README.md`
- [ ] `mobile/ios/RunnerTests/RunnerTests.swift`
- [ ] `mobile/linux/.gitignore`
- [ ] `mobile/linux/CMakeLists.txt`
- [ ] `mobile/linux/flutter/CMakeLists.txt` (generated Flutter integration)
- [ ] `mobile/linux/runner/CMakeLists.txt`
- [ ] `mobile/linux/runner/main.cc` (Flutter runner scaffold)
- [ ] `mobile/linux/runner/my_application.cc` (Flutter runner scaffold)
- [ ] `mobile/linux/runner/my_application.h` (Flutter runner scaffold)
- [ ] `mobile/macos/.gitignore`
- [ ] `mobile/macos/Flutter/Flutter-Debug.xcconfig`
- [ ] `mobile/macos/Flutter/Flutter-Release.xcconfig`
- [ ] `mobile/macos/Runner.xcodeproj/project.pbxproj`
- [ ] `mobile/macos/Runner.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- [ ] `mobile/macos/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme`
- [ ] `mobile/macos/Runner.xcworkspace/contents.xcworkspacedata`
- [ ] `mobile/macos/Runner.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist`
- [ ] `mobile/macos/Runner/AppDelegate.swift`
- [ ] `mobile/macos/Runner/Info.plist`
- [ ] `mobile/macos/Runner/MainFlutterWindow.swift`
- [ ] `mobile/macos/Runner/Base.lproj/MainMenu.xib`
- [ ] `mobile/macos/Runner/Configs/AppInfo.xcconfig`
- [ ] `mobile/macos/Runner/Configs/Debug.xcconfig`
- [ ] `mobile/macos/Runner/Configs/Release.xcconfig`
- [ ] `mobile/macos/Runner/Configs/Warnings.xcconfig`
- [ ] `mobile/macos/Runner/DebugProfile.entitlements`
- [ ] `mobile/macos/Runner/Release.entitlements`
- [ ] `mobile/macos/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json`
- [ ] `mobile/macos/RunnerTests/RunnerTests.swift`
- [ ] `mobile/web/index.html`
- [ ] `mobile/web/manifest.json`
- [ ] `mobile/windows/.gitignore`
- [ ] `mobile/windows/CMakeLists.txt`
- [ ] `mobile/windows/flutter/CMakeLists.txt` (generated Flutter integration)
- [ ] `mobile/windows/runner/CMakeLists.txt`
- [ ] `mobile/windows/runner/Runner.rc`
- [ ] `mobile/windows/runner/flutter_window.cpp` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/flutter_window.h` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/main.cpp` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/resource.h`
- [ ] `mobile/windows/runner/runner.exe.manifest`
- [ ] `mobile/windows/runner/utils.cpp` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/utils.h` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/win32_window.cpp` (Flutter runner scaffold)
- [ ] `mobile/windows/runner/win32_window.h` (Flutter runner scaffold)

### Infrastructure, CI/CD, monitoring and docs

- [ ] `infra/terraform/main.tf`
- [ ] `infra/terraform/variables.tf`
- [ ] `infra/terraform/outputs.tf`
- [ ] `infra/terraform/terraform.tfvars.example`
- [ ] `infra/terraform/.terraform.lock.hcl`
- [ ] `infra/cloudformation/cipherpage-staging-stack.yaml`
- [ ] `infra/serverless/lambda_thumbnail_generator.py`
- [ ] `deploy/docker/Dockerfile.jenkins`
- [ ] `deploy/docker/docker-compose.jenkins.yml`
- [ ] `deploy/docker/docker-compose.monitoring.yml`
- [ ] `deploy/jenkins/Jenkinsfile`
- [ ] `monitoring/prometheus/prometheus.yml`
- [ ] `monitoring/prometheus/alert.rules.yml`
- [ ] `monitoring/grafana/provisioning/datasources/prometheus.yml`
- [ ] `monitoring/grafana/provisioning/dashboards/dashboard_provider.yml`
- [ ] `monitoring/grafana/dashboards/cipherpage_overview.json`
- [ ] `scripts/verify_pipeline.ps1`
- [ ] `scripts/verify_pipeline.sh`
- [ ] `scripts/validate_infra.ps1`
- [ ] `scripts/validate_infra.sh`
- [ ] `docs/runbooks/ci_cd_runbook.md`
- [ ] `docs/runbooks/aws_deployment_runbook.md`
- [ ] `docs/runbooks/observability_runbook.md`
- [ ] `docs/runbooks/backup_and_recovery_runbook.md`

## 8. Recommended audit sequence

1. Reproducibility and environment contract: reconcile READMEs, env examples, lockfiles, container targets and CI commands.
2. Database contract: compare ORM models, all Alembic revisions, seeding and deletion/retention behavior.
3. Authentication and API authorization: trace Supabase JWT validation, local user sync, role checks, CORS, rate limiting and every route.
4. Core backend flows: courses/enrollment/progress/gamification and payments.
5. Submission pipeline: API acceptance, queue/broker failure path, worker lifecycle and code-runner isolation on each runtime.
6. AI/RAG: provider selection/fallback, quota accounting, ingestion, embedding compatibility, enrollment filtering, prompt safety and citation behavior.
7. Web integration: actual versus fixture-backed pages, Supabase session/localStorage behavior, API URL/token fallback and error states.
8. Mobile integration: platform configuration, Supabase initialization, backend base URL, session sync and current widget coverage.
9. Deployment/IaC: reconcile Terraform, CloudFormation, Compose and runbooks; specifically validate public/private subnet placement, Redis and Celery deployment, secret injection, database backups and Lambda wiring.
10. CI and operations: align duplicate Jenkinsfiles and documented test counts; then review metrics, alerts, dashboard and runbook claims.
11. Once disposable Postgres/Redis/API services and provider dependencies are available, run the stateful backend integration suite in isolation and repeat platform builds.
