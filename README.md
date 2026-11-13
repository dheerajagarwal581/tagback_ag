# QR-Based Temporary Communication & Lost-and-Found Platform

[![Status](https://img.shields.io/badge/Status-Architecture%20%26%20Planning-blue)]()
[![Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-emerald)]()
[![Privacy](https://img.shields.io/badge/Privacy-First-purple)]()

A modern, privacy-preserving lost-and-found communication system. The platform allows registered owners to generate a single, permanent QR code for their belongings. When someone finds a lost item, they scan the QR code to open an anonymous, account-free web portal and initiate a dedicated temporary chat room with the owner—without either party disclosing personal phone numbers or email addresses.

---

## 📌 Table of Contents

- [Core Value Proposition](#-core-value-proposition)
- [System Highlights & Key Features](#-system-highlights--key-features)
- [Architecture Overview](#-architecture-overview)
- [Technology Stack](#-technology-stack)
- [Repository Structure](#-repository-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
  - [1. Clone and Configure Environment](#1-clone-and-configure-environment)
  - [2. Database Setup (PostgreSQL)](#2-database-setup-postgresql)
  - [3. Backend Setup (FastAPI)](#3-backend-setup-fastapi)
  - [4. Frontend Setup (Next.js)](#4-frontend-setup-nextjs)
- [Running the Application](#-running-the-application)
- [Running Tests](#-running-tests)
- [Documentation Index](#-documentation-index)
- [Development Principles & Rules](#-development-principles--rules)

---

## 💡 Core Value Proposition

Traditional lost-and-found methods present major privacy and friction challenges:
- Writing phone numbers or emails on physical tags exposes sensitive personal info to anyone who looks.
- Messaging apps require mutual contact exchange and account creation.
- Finders often do not know how to contact the owner quickly.

**The Solution:**
1. **One Permanent QR Code:** The owner attaches one unique QR code to all their belongings (keys, laptop, backpack, luggage).
2. **Account-Free Finder Access:** Finders scan the code using a standard smartphone camera to view the owner's public profile and submit a contact request.
3. **Independent Temporary Rooms:** Each finder session generates an isolated, secure temporary chat room.
4. **Owner-Controlled Acceptance:** Owners review pending requests and decide whether to accept, reject, or block.
5. **Session Recovery:** Finders receive a secure one-click recovery link allowing them to resume active conversations without an account.
6. **Instant Revocation:** Once marked as recovered or closed, chat channels and recovery credentials are permanently revoked.

---

## 🚀 System Highlights & Key Features

- **Permanent Digital Identity:** Cryptographically unguessable public QR tokens.
- **True Guest Anonymity:** Zero app installs, zero sign-ups for finders.
- **Multi-Tenant Room Isolation:** Different finders can contact the same owner concurrently without crosstalk.
- **Smart Room Reuse:** Re-scanning by the same active guest session returns them to their existing conversation.
- **Real-Time WebSockets:** Instant bidirectional messaging with delivery state tracking.
- **In-App & Asynchronous Notifications:** Immediate visual alerts for owners upon new requests.
- **Strict Privacy Controls:** Owner email and phone numbers are never transmitted to public clients.

---

## 🏛 Architecture Overview

```text
       +-----------------------+              +-----------------------+
       |     OWNER (Browser)   |              |    FINDER (Mobile)    |
       +-----------+-----------+              +-----------+-----------+
                   |                                      |
                   | Authenticated Session                | Anonymous Scan
                   v                                      v
       +-----------------------+              +-----------------------+
       |   Owner Dashboard     |              |   Public QR Profile   |
       |  (Next.js App Router) |              |  (Next.js App Router) |
       +-----------+-----------+              +-----------+-----------+
                   |                                      |
                   +------------------+-------------------+
                                      |
                                      | REST / WebSockets (JSON)
                                      v
                      +-------------------------------+
                      |     FastAPI Backend API       |
                      |   - Auth & Session Manager    |
                      |   - QR Code Service (qrcode)  |
                      |   - Room & Lifecycle Manager  |
                      |   - WebSocket Hub             |
                      |   - Security & Rate Limiter   |
                      +---------------+---------------+
                                      |
                                      | SQLAlchemy 2.0 (Async)
                                      v
                      +-------------------------------+
                      |     PostgreSQL Database       |
                      |  (Users, Profiles, QR, Rooms, |
                      |   Messages, Notifications)    |
                      +-------------------------------+
```

---

## 🛠 Technology Stack

| Layer | Technology | Key Capabilities |
|---|---|---|
| **Frontend** | [Next.js](https://nextjs.org/) (React 18+, App Router) | Server-side rendering, client interactive chat |
| **Language (FE)**| [TypeScript](https://www.typescriptlang.org/) | Strict type definitions across UI and API payloads |
| **Styling** | [Tailwind CSS](https://tailwindcss.com/) | Mobile-first, responsive, accessible design |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) | High-performance asynchronous REST and WebSockets |
| **Database** | [PostgreSQL](https://www.postgresql.org/) | Relational integrity, foreign keys, indexes |
| **ORM & Migrations**| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/) | Async queries, schema migrations |
| **Real-time** | Native WebSockets | Low-latency bi-directional messaging |
| **QR Generation** | Python `qrcode[pil]` | PNG/SVG generation with unguessable tokens |
| **Testing** | [Pytest](https://pytest.org/) & [Playwright](https://playwright.dev/) | Unit, integration, security, and E2E browser tests |

---

## 📂 Repository Structure

```text
qr-temporary-communication/
│
├── README.md                      # Project introduction, setup, architecture
├── AGENTS.md                      # Instructions and constraints for AI agents
├── .gitignore                     # Git ignore rules for Python, Node, OS
├── .env.example                   # Complete configuration template
│
├── docs/                          # Core system specifications
│   ├── PROJECT_OVERVIEW.md        # Problem statement, solution, user roles
│   ├── REQUIREMENTS.md            # Functional & non-functional requirements
│   ├── TECH_STACK.md              # Technology stack justifications & constraints
│   ├── SYSTEM_ARCHITECTURE.md     # Component diagrams, sequence flows, data flows
│   ├── DATABASE_SCHEMA.md         # Schema design, entity relations, indexes
│   ├── API_DOCUMENTATION.md       # REST endpoints, WebSocket protocols, schemas
│   ├── USER_FLOWS.md              # Step-by-step user interaction walkthroughs
│   ├── SECURITY.md                # Threat models, auth, encryption, rate limits
│   └── DECISIONS.md               # Architectural Decision Records (ADRs)
│
├── planning/                      # Project execution management
│   ├── PLAN.md                    # Detailed step-by-step development plan
│   ├── ROADMAP.md                 # Development phases and timeline
│   ├── TASKS.md                   # Granular tasks with priority and status
│   ├── MILESTONES.md              # Checkpoints and verification criteria
│   └── MVP_SCOPE.md               # Strict in-scope vs out-of-scope boundaries
│
├── tracking/                      # Progress and quality tracking
│   ├── PROGRESS.md                # Real-time implementation status
│   ├── CHANGELOG.md               # Historic log of changes and decisions
│   ├── BUGS.md                    # Known issues, severity, and resolution log
│   └── TESTING_REPORT.md          # Test matrices, coverage, and results
│
├── prompts/                       # Guided prompt templates for AI-assisted dev
│   ├── PROJECT_SETUP.md           # Environment & scaffolding setup prompt
│   ├── IMPLEMENTATION.md          # Feature implementation prompt
│   ├── CODE_REVIEW.md             # Code review & verification prompt
│   └── DEBUGGING.md               # Root cause analysis prompt
│
├── frontend/                      # (Future) Next.js App Router frontend
├── backend/                       # (Future) FastAPI backend application
└── tests/                         # (Future) Test suites (Unit, E2E)
```

---

## ⚙ Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Node.js**: v18.17+ or v20+ (`node -v`)
- **Package Manager**: npm, pnpm, or yarn
- **Python**: v3.11+ (`python --version`)
- **PostgreSQL**: v14+ running locally or in Docker (`psql --version`)
- **Git**: v2.30+

---

## 📦 Installation & Setup

### 1. Clone and Configure Environment

```bash
# Clone the repository
git clone https://github.com/your-username/qr-temporary-communication.git
cd qr-temporary-communication

# Copy the example environment file
cp .env.example .env
```

Review and adjust variables in `.env` as needed (e.g. database credentials).

### 2. Database Setup (PostgreSQL)

Create the database locally:
```bash
# Using PostgreSQL CLI
psql -U postgres -c "CREATE DATABASE qr_lost_found;"
```

### 3. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### 4. Frontend Setup (Next.js)

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Build or run development server
npm run dev
```

---

## 🏃 Running the Application

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *FastAPI Interactive Docs:* [http://localhost:8000/docs](http://localhost:8000/docs)

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   *Frontend Application:* [http://localhost:3000](http://localhost:3000)

---

## 🧪 Running Tests

```bash
# Backend Unit & Integration Tests
cd backend
pytest -v --cov=app tests/

# Frontend E2E / Component Tests
cd frontend
npm test
```

---

## 📚 Documentation Index

For in-depth architectural and operational specifications, consult:

| Document | Purpose |
|---|---|
| [PROJECT_OVERVIEW.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/PROJECT_OVERVIEW.md) | High-level problem statement, objectives, and domain concepts |
| [REQUIREMENTS.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/REQUIREMENTS.md) | Full functional (FR) and non-functional (NFR) requirements |
| [TECH_STACK.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/TECH_STACK.md) | Technical stack components, decisions, and constraints |
| [SYSTEM_ARCHITECTURE.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/SYSTEM_ARCHITECTURE.md) | Component architecture, sequence diagrams, and real-time flows |
| [DATABASE_SCHEMA.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/DATABASE_SCHEMA.md) | Relational database schema, ER diagrams, foreign keys, and indexes |
| [API_DOCUMENTATION.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/API_DOCUMENTATION.md) | Comprehensive REST endpoints, WebSocket schema, and payload specs |
| [USER_FLOWS.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/USER_FLOWS.md) | Detailed UX workflows for Owners and Anonymous Finders |
| [SECURITY.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/SECURITY.md) | Threat modeling, cryptographic hashing, auth tokens, rate limits |
| [DECISIONS.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/docs/DECISIONS.md) | Architectural Decision Records (ADRs) |
| [PLAN.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/planning/PLAN.md) | Step-by-step phased development plan |
| [TASKS.md](file:///c:/Users/adity/OneDrive/Desktop/Hack/take1/qr-temporary-communication/planning/TASKS.md) | Actionable task breakdown with priority ratings |

---

## ⚖ Development Principles & Rules

1. **Documentation First**: All architectural questions and workflows must be codified in documentation prior to writing application code.
2. **Explicit Approval**: Implementation cannot start without explicit user authorization.
3. **Privacy by Design**: Sensitive owner credentials and contact info must never be leaked through QR codes or API responses.
4. **Resilience & Security**: Validate inputs on the backend; enforce room-level authorization for all REST and WebSocket messages.
