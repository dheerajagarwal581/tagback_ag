# AGENTS.md — Persistent Instructions for AI Coding Agents

> **Project:** QR-Based Temporary Communication & Lost-and-Found Platform  
> **Status:** Architecture & Planning Phase (Implementation On Hold Pending User Approval)  
> **Target Audience:** All AI agents, subagents, and human contributors working on this codebase.

---

## 1. Core Operating Directive

You are working as an AI Software Engineer and System Architect on this codebase.
**Strict Rule:** You MUST NOT write application code or make major architectural changes without explicit approval from the project owner.

Always follow the principle of:
1. **Understand** the spec and inputs completely.
2. **Document and Plan** before writing code.
3. **Get Approval** before executing changes.
4. **Implement Incrementally** with tests and verification.

---

## 2. Non-Negotiable Architecture Rules

1. **Technology Stack Preservation**:
   - Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic, WebSockets, Python `qrcode`.
   - Frontend: Next.js (App Router), TypeScript, Tailwind CSS.
   - Database: PostgreSQL (asyncpg driver).
   - *Do not substitute these frameworks, do not introduce Redis, Kafka, or microservices without explicit instruction.*

2. **Core Domain Model**:
   - **One permanent QR identity per owner account**. A user attaches this single QR code to multiple physical items.
   - **Finder is strictly anonymous and account-free**. Finders scan the QR code, view the public owner profile, and submit a contact request.
   - **Independent Temporary Rooms**: Every finder session creates an isolated temporary chat room (`Room`). Different finders never see each other's messages, items, or identities.
   - **Room Reuse**: If an authorized returning guest with an active room scans the owner's QR again, reuse that active room rather than creating clutter.
   - **Owner Controls Acceptance**: Finders can send initial messages while a room is `Pending`, but the Owner MUST accept the request before replying.
   - **Revocation on Closure**: Once a room is `Closed`, `Rejected`, or marked `Recovered`, all messaging is terminated and guest recovery credentials are permanently revoked.

3. **Backend-Enforced Authorization**:
   - Never trust frontend route guards or UI hiding for security.
   - Every REST endpoint and every WebSocket connection must strictly authenticate and authorize room membership on the server.
   - Room data isolation is paramount. SQL queries must always filter by `owner_id` or authorized `guest_session_id`.

4. **Privacy First**:
   - Owner's email, phone number, and internal database IDs must NEVER be returned to the public or finder APIs.
   - Public QR profile displays only owner-configured public display name and optional bio/image.
   - Email notifications (Phase 2) must contain only metadata and dashboard links—never conversation transcripts.

5. **No Blind Hallucinations / Feature Creep**:
   - Do not implement AI recognition, voice/video calls, multi-QR management, or payment gateways unless explicitly commanded.
   - Keep the MVP focused strictly on the lost-and-found communication lifecycle.

---

## 3. Code Quality and Engineering Standards

### 3.1 Backend Standards (Python / FastAPI)
- **Directory Structure**: Layered modular structure:
  - `app/api/v1/endpoints/`: Routing and request validation.
  - `app/core/`: Configuration (`config.py`), security (`security.py`), database engine (`database.py`).
  - `app/models/`: SQLAlchemy 2.0 declarative models with type annotations (`Mapped[...]`).
  - `app/schemas/`: Pydantic V2 schemas for request validation and response serialization.
  - `app/services/`: Pure business logic (room management, QR generation, auth).
  - `app/websocket/`: WebSocket connection manager and event handlers.
- **Async First**: Use async database sessions (`AsyncSession`), async endpoint handlers, and async WebSocket message broadcasting.
- **Error Handling**: Use custom HTTPException handlers with structured JSON error details `{"detail": "...", "code": "..."}`. Avoid catch-all generic exceptions that swallow stack traces.
- **Migrations**: Every schema modification must have a corresponding Alembic migration script.

### 3.2 Frontend Standards (Next.js / TypeScript / Tailwind)
- **App Router**: Follow Next.js App Router conventions (`app/(auth)`, `app/(dashboard)`, `app/q/[token]`, `app/room/[roomId]`).
- **Strict Typing**: No `any`. Declare strict interfaces for API responses, WebSocket messages, and component props.
- **Component Separation**: Separate server components (data fetching) from client components (`"use client"` for WebSocket chat and forms).
- **Responsive & Mobile-Optimized**: Mobile-first UI using Tailwind CSS. Finders will 90%+ of the time scan from mobile devices. Ensure tap targets, forms, and chat inputs are touch-friendly.
- **Design Consistency**: Follow `refrences/UI_REFERENCE.md` for status colors, buttons, form controls, and loading/empty states.

---

## 4. Testing & Verification Mandate

Before claiming any task is complete:
1. **Automated Verification**:
   - Run unit tests: `pytest tests/`
   - Run linter/type-checker: `ruff check` / `mypy` / `npm run lint`
   - Verify that test output is captured and verified before claiming success.
2. **Critical Security Tests**:
   - Verify that User B cannot access Room A (403/404).
   - Verify that Guest B cannot read Guest A's messages.
   - Verify that closed rooms reject new messages.
   - Verify that recovery link validation succeeds with valid token and fails with tampered/expired token.

---

## 5. Development Workflow for Agents

When instructed to work on a task:
1. **Check Tracking & Documentation**: Read `planning/TASKS.md`, `planning/PLAN.md`, and `tracking/PROGRESS.md`.
2. **Review Relevant Spec Files**:
   - `docs/SYSTEM_ARCHITECTURE.md`
   - `docs/DATABASE_SCHEMA.md`
   - `docs/API_DOCUMENTATION.md`
   - `docs/SECURITY.md`
3. **Execute Task in Isolation**:
   - Write tests first where applicable.
   - Implement minimal required code.
   - Run tests and fix any regressions.
4. **Update Tracking**:
   - Check off task item in `planning/TASKS.md`.
   - Record note in `tracking/PROGRESS.md` or `tracking/CHANGELOG.md`.
   - Never mark something done if it hasn't passed verification.

---

## 6. Prohibited Actions

- **DO NOT** commit `.env` or any production secrets.
- **DO NOT** remove or skip tests to make builds pass.
- **DO NOT** create orphan database columns without migration files.
- **DO NOT** expose database primary key integers directly to public routes; use UUIDs or cryptographically random tokens (`public_token`, `room_id`).
- **DO NOT** install npm or pip packages that are not listed in `docs/TECH_STACK.md` without explanation and approval.
