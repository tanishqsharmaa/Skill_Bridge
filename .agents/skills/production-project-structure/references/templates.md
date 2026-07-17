# Project Templates

> Four copy-paste-ready project templates for different use cases.
> Each template is production-validated and can be used as a starting point.

---

## Template A — Full-Stack SaaS (TypeScript, Next.js + FastAPI)

Use when: Building a SaaS product with a Next.js frontend and FastAPI backend.

```
my-saas/
├── apps/
│   ├── web/                         # Next.js 14 App Router
│   │   └── src/
│   │       ├── app/                 # Routes (App Router)
│   │       │   ├── (auth)/          # Auth route group
│   │       │   ├── (dashboard)/     # Dashboard route group
│   │       │   ├── layout.tsx
│   │       │   └── page.tsx
│   │       ├── features/            # Feature-Sliced Design
│   │       │   ├── auth/
│   │       │   ├── billing/
│   │       │   └── dashboard/
│   │       └── shared/
│   │           ├── ui/              # App-specific components (not in packages/ui)
│   │           └── lib/
│   └── api/                         # FastAPI backend
│       └── src/
│           ├── users/               # Domain module
│           │   ├── router.py
│           │   ├── service.py
│           │   ├── repository.py
│           │   ├── schemas.py
│           │   └── models.py
│           ├── billing/
│           │   └── ... (same structure)
│           ├── core/
│           │   ├── config.py
│           │   ├── database.py
│           │   └── security.py
│           └── main.py
├── packages/
│   ├── ui/                          # React components (shared design system)
│   │   └── src/
│   │       ├── button/
│   │       ├── modal/
│   │       ├── form/
│   │       └── index.ts
│   ├── types/                       # Shared Pydantic/TS DTOs
│   │   └── src/
│   │       ├── user.ts
│   │       ├── billing.ts
│   │       └── index.ts
│   └── utils/
│       └── src/
│           ├── date.ts
│           ├── format.ts
│           └── index.ts
├── tooling/
│   ├── eslint-config/
│   │   ├── base.js
│   │   ├── next.js
│   │   └── package.json
│   └── typescript-config/
│       ├── base.json
│       ├── nextjs.json
│       └── package.json
├── infra/
│   └── terraform/
│       ├── modules/
│       └── environments/
│           ├── dev/
│           ├── staging/
│           └── prod/
├── docs/
│   └── adr/
│       └── README.md
├── turbo.json
├── pnpm-workspace.yaml
├── package.json
└── .github/
    ├── CODEOWNERS
    └── workflows/
        ├── ci.yml
        └── release.yml
```

---

## Template B — Multi-App Design System Platform (Frontend Monorepo)

Use when: Building a shared component library consumed by multiple frontend apps.

```
design-platform/
├── apps/
│   ├── docs/                        # Documentation site (Storybook / Docusaurus)
│   │   └── stories/
│   ├── playground/                  # Live component playground
│   └── admin/                       # Internal admin tool
├── packages/
│   ├── core/                        # Tokens, theme, CSS variables
│   │   └── src/
│   │       ├── tokens/
│   │       ├── theme/
│   │       └── index.ts
│   ├── ui-base/                     # Primitive components (Button, Input, Modal)
│   │   └── src/
│   │       ├── button/
│   │       │   ├── Button.tsx
│   │       │   ├── Button.test.tsx
│   │       │   └── index.ts
│   │       ├── input/
│   │       ├── modal/
│   │       └── index.ts
│   ├── ui-patterns/                 # Composite components (DataTable, Form)
│   │   └── src/
│   │       ├── data-table/
│   │       ├── form/
│   │       └── index.ts
│   └── icons/                       # SVG icon library
│       └── src/
│           └── index.ts
├── tooling/
│   ├── eslint-config/
│   ├── typescript-config/
│   └── prettier-config/
├── turbo.json
├── pnpm-workspace.yaml
└── .github/CODEOWNERS
```

---

## Template C — Python AI / Agentic RAG System

Use when: Building a production RAG pipeline or agentic AI system.

```
rag-system/
├── src/
│   ├── agents/
│   │   └── research/
│   │       ├── graph.py
│   │       ├── nodes.py
│   │       ├── state.py
│   │       └── tools.py
│   ├── retrieval/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── runner.py
│   ├── prompts/
│   │   ├── system/
│   │   │   ├── researcher.md
│   │   │   └── summarizer.md
│   │   └── few_shot/
│   │       └── extraction_examples.md
│   ├── api/
│   │   ├── routers/
│   │   │   └── query.py
│   │   └── middleware/
│   └── core/
│       ├── config.py
│       └── llm_client.py
├── evals/
│   ├── fixtures/
│   │   └── golden_dataset.json
│   ├── test_retrieval.py
│   └── test_generation.py
├── notebooks/
│   └── exploratory/               # Never imported by src/
├── scripts/
│   ├── ingest.py
│   └── build_index.py
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   └── adr/
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## Template D — Microservices Platform (Monorepo model)

Use when: Multiple backend services, same team, shared types and tooling.

```
my-platform/
├── services/
│   ├── user-service/
│   │   ├── src/
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   └── repositories/  # Interfaces, not implementations
│   │   │   ├── application/
│   │   │   │   ├── use-cases/
│   │   │   │   └── dtos/
│   │   │   ├── infrastructure/
│   │   │   │   ├── persistence/   # DB implementations
│   │   │   │   └── http/          # HTTP adapters
│   │   │   └── main.ts
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── package.json
│   ├── order-service/
│   │   └── ... (same structure as user-service)
│   └── notification-service/
│       └── ...
├── libs/                            # Shared internal libraries
│   ├── proto/                       # Protobuf definitions (gRPC contracts)
│   ├── events/                      # Event schemas (Kafka/SNS)
│   └── observability/               # Shared tracing setup
├── infra/
│   ├── k8s/
│   │   ├── base/
│   │   └── overlays/
│   │       ├── dev/
│   │       └── prod/
│   └── terraform/
├── docs/
│   └── adr/
├── .github/
│   ├── CODEOWNERS
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
└── turbo.json
```

---

## First Steps for Each Template

After choosing a template, here are the first three actions to take:

**Template A (Full-Stack SaaS):**
1. Create `pnpm-workspace.yaml` defining `apps/*`, `packages/*`, `tooling/*`
2. Create `tooling/typescript-config` with `base.json` and `nextjs.json`
3. Scaffold `packages/types` first — it's the contract between frontend and backend

**Template B (Design System):**
1. Set up `packages/core` with design tokens — everything else depends on this
2. Create `tooling/eslint-config` with Storybook rules
3. Set up `apps/docs` pointing to the packages — validates the API surface early

**Template C (AI/RAG):**
1. Set up `core/config.py` with all environment variables — every module will need it
2. Create the `prompts/system/` directory with your first versioned prompt — establish the pattern early
3. Set up `evals/fixtures/golden_dataset.json` with even 5 examples — CI-gate retrieval quality from day 1

**Template D (Microservices):**
1. Define `libs/proto/` contracts *before* writing any service code — services depend on these
2. Set up `libs/observability/` with shared tracing — impossible to add retroactively across services
3. Create `.github/CODEOWNERS` — assign service ownership before the first commit
