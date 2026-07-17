# Stack-Specific Patterns

> Source: Feature-Sliced Design documentation (feature-sliced.design), FastAPI official docs,
> DSI Innovators, auth0.com FastAPI best practices, LangGraph production conventions,
> LlamaIndex + LangGraph data-plane/control-plane split (2025–2026).

This file contains production-validated blueprints for six major project types.
Jump directly to the section matching the user's stack.

---

## Table of Contents

- [6a. Frontend-Only (React / Vue / Next.js)](#6a-frontend-only)
- [6b. Backend-Only (FastAPI / Node.js / Go)](#6b-backend-only)
- [6c. Full-Stack Applications](#6c-full-stack)
- [6d. Published Libraries / Packages](#6d-published-libraries)
- [6e. Microservices](#6e-microservices)
- [6f. AI / RAG / Agentic Applications](#6f-ai-rag-agentic)

---

## 6a. Frontend-Only

For single-app frontend projects, **Feature-Sliced Design (FSD)** is the most mature and widely
validated methodology as of 2025. It defines six layers with strict one-directional import rules:

```
src/
├── app/          # Entry point, providers, routing, global styles
├── pages/        # Route-level components assembled from lower layers
├── widgets/      # Large self-contained UI blocks (e.g., LoginForm, Sidebar)
├── features/     # User interactions tied to a business capability (e.g., AddToCart)
├── entities/     # Business objects with their UI/model/API (e.g., User, Product)
└── shared/       # Reusable kit: UI primitives, helpers, config, types
```

**Import rule**: Each layer may only import from layers *below* it. `features` may import from
`entities` and `shared`. `entities` may import from `shared` only. No layer imports from above it.

Each layer contains **slices** (business domains, e.g., `user/`, `cart/`) and each slice contains
**segments** (`ui/`, `model/`, `api/`, `lib/`).

**Example slice:**
```
features/
└── add-to-cart/
    ├── ui/
    │   └── AddToCartButton.tsx
    ├── model/
    │   └── useAddToCart.ts
    ├── api/
    │   └── addToCart.ts
    └── index.ts   ← public API
```

---

## 6b. Backend-Only

### Domain-Driven Structure (FastAPI / Node.js)

For large FastAPI applications, the consensus is a **domain-driven structure** where each business
domain is a self-contained package:

```
src/
├── main.py                    # FastAPI app instantiation, lifespan, router registration
├── core/                      # Cross-cutting: config, security, database session
│   ├── config.py
│   ├── database.py
│   └── security.py
├── users/                     # User domain — self-contained
│   ├── router.py              # HTTP endpoints
│   ├── service.py             # Business logic
│   ├── repository.py          # Database queries
│   ├── schemas.py             # Pydantic request/response models
│   ├── models.py              # SQLAlchemy ORM models
│   └── tests/
├── orders/                    # Order domain — same structure
│   └── ...
└── shared/                    # Cross-domain: base models, exceptions, utilities
    ├── exceptions.py
    └── utils.py
```

**Anti-pattern to avoid:** A flat structure that groups all routers in one file and all models
in another. This becomes unmanageable past 10–15 endpoints.

### Clean Architecture / Hexagonal (Higher Complexity)

```
src/
├── domain/                    # Core: entities, value objects, repository interfaces
├── application/               # Use cases, command handlers, DTOs
├── infrastructure/            # Adapters: DB, HTTP clients, queues
│   ├── persistence/
│   ├── http/
│   └── messaging/
└── presentation/              # FastAPI routers, CLI handlers, gRPC handlers
```

**The golden rule:** Dependency arrows point inward. `infrastructure` implements `domain`
interfaces. `domain` never imports `infrastructure`.

### Go Projects

```
my-service/
├── cmd/
│   └── server/
│       └── main.go            # Entry point per binary
├── internal/                  # Private application code (cannot be imported externally)
│   ├── domain/
│   ├── handler/
│   ├── repository/
│   └── service/
├── pkg/                       # Public library code (can be imported by other Go modules)
├── api/                       # API definitions (OpenAPI, Protobuf)
├── configs/
└── scripts/
```

---

## 6c. Full-Stack Applications

Recommended structure for a full-stack monorepo (Next.js + FastAPI example):

```
my-app/
├── apps/
│   ├── web/                   # Next.js (frontend)
│   └── api/                   # FastAPI (backend)
├── packages/
│   ├── types/                 # Shared DTOs and API types (TypeScript)
│   ├── ui/                    # Shared UI components
│   └── utils/                 # Shared pure utilities
└── tooling/
```

The `types/` package is the contract between frontend and backend. It is the only shared runtime
code between the two. Generate it from OpenAPI specs or Pydantic schemas to keep it in sync.

---

## 6d. Published Libraries / Packages

```
my-library/
├── src/
│   ├── index.ts               # Public API — everything exported here
│   ├── core/                  # Internal implementation
│   └── utils/                 # Internal utilities
├── tests/
│   ├── unit/
│   └── integration/
├── examples/                  # Usage examples
├── docs/
├── package.json
├── tsup.config.ts             # Build config (tsup, rollup, or esbuild)
└── CHANGELOG.md
```

**Rules:**
- Never export internal implementation files.
- Ship two build targets: ESM and CJS.
- Peer-declare framework dependencies (React, Vue).
- Provide separate type exports.

---

## 6e. Microservices

Each microservice is a fully independent deployable unit. Two valid organizational models:

**Model A — Polyrepo (one repo per service):** Preferred when services have different tech stacks,
different release cadences, or different team ownership. Drawback: shared tooling sync cost.

**Model B — Monorepo (all services in one repo):** Preferred when services share types, use the
same stack, and are owned by the same team or platform.

**Per-service structure:**

```
order-service/
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   │   ├── http/              # Incoming: Express/FastAPI routers
│   │   ├── persistence/       # Outgoing: DB adapters
│   │   └── messaging/         # Outgoing: Kafka/SQS producers
│   └── main.ts
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── docker-compose.yml
└── package.json
```

Service boundaries should be defined around **business capabilities** (Bounded Contexts in DDD),
not technical layers. A "user service" that does profiles AND authentication AND permissions is too
broad. A "user profile service" is appropriately scoped.

---

## 6f. AI / RAG / Agentic Applications

This is an emerging pattern. Based on LangGraph's production conventions and the LlamaIndex +
LangGraph data-plane/control-plane split.

```
my-rag-agent/
├── src/
│   ├── agents/                # LangGraph state graphs, graph definitions
│   │   ├── research_agent/
│   │   │   ├── graph.py       # StateGraph definition
│   │   │   ├── nodes.py       # Individual node functions
│   │   │   ├── state.py       # Typed state schema
│   │   │   └── tools.py       # Agent tools
│   │   └── orchestrator/
│   │
│   ├── retrieval/             # Data plane: chunking, embedding, retrieval
│   │   ├── chunking/
│   │   ├── embeddings/
│   │   ├── vector_store/      # Qdrant / pgvector adapters
│   │   └── reranking/
│   │
│   ├── evaluation/            # RAGAS evals, CI-gated tests
│   │   ├── datasets/
│   │   ├── metrics.py
│   │   └── run_evals.py
│   │
│   ├── prompts/               # Versioned prompt templates
│   │   ├── system/
│   │   └── few_shot/
│   │
│   ├── observability/         # LangSmith / OpenTelemetry wiring
│   │   └── tracing.py
│   │
│   ├── api/                   # FastAPI serving layer
│   │   ├── routers/
│   │   └── middleware/
│   │
│   └── core/                  # Config, model clients, shared utilities
│       ├── config.py
│       └── llm_client.py
│
├── evals/                     # Standalone eval harness (CI-runnable)
│   ├── fixtures/              # Golden datasets
│   ├── test_retrieval.py
│   └── test_generation.py
│
├── notebooks/                 # Exploratory work (not production)
│
└── scripts/
    ├── ingest.py              # Data ingestion pipeline
    └── build_index.py         # Index construction
```

**Key AI-specific rules:**
- Prompts are versioned artifacts, not inline strings. Store in `prompts/` and load like configs.
- Eval datasets are fixtures — checked in, versioned, never modified without a PR.
- Notebooks are ephemeral exploration — never import from application code, never depended upon.
- Retrieval (data plane) and orchestration (control plane) are separate concerns in distinct modules.
