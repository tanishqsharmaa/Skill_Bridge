# Monorepo Blueprint — JS/TS (Turborepo + pnpm)

> Source: Turborepo official documentation (turbo.build), Nx conventions, pnpm workspace docs,
> and engineering blogs from Vercel and the Nx team (2025–2026).

This is the production-grade JS/TS monorepo structure recommended by Turborepo official docs,
validated by Nx conventions and the pnpm ecosystem.

---

## Full Directory Tree

```
my-platform/
│
├── apps/                          # Deployable application packages
│   ├── web/                       # Next.js / Vite consumer app
│   ├── api/                       # FastAPI / Express service
│   ├── admin/                     # Internal admin panel
│   └── mobile/                    # React Native app
│
├── packages/                      # Internal library packages (not deployable)
│   │
│   ├── ui/                        # Design system: presentational components only
│   │   ├── src/
│   │   │   ├── button/
│   │   │   ├── modal/
│   │   │   └── index.ts           # Public API surface
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── domain/                    # Core business logic (no framework deps)
│   │   ├── src/
│   │   │   ├── user/
│   │   │   ├── order/
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── data-access/               # API clients, DB clients, state management
│   │   ├── src/
│   │   │   ├── user-api/
│   │   │   ├── order-api/
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── utils/                     # Pure utility functions (no framework, no domain)
│   │   ├── src/
│   │   │   ├── date/
│   │   │   ├── format/
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   └── types/                     # Shared TypeScript types, interfaces, DTOs
│       ├── src/
│       │   └── index.ts
│       └── package.json
│
├── tooling/                       # Build-time tooling (not runtime)
│   ├── eslint-config/             # @repo/eslint-config
│   ├── typescript-config/         # @repo/typescript-config
│   └── prettier-config/           # @repo/prettier-config
│
├── infra/                         # IaC: Terraform, Pulumi, CDK
│   ├── modules/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
│
├── scripts/                       # Repository-level automation scripts
│   ├── seed-db.ts
│   ├── generate-schema.ts
│   └── release.sh
│
├── docs/                          # Documentation and decision records
│   ├── adr/                       # Architecture Decision Records
│   │   ├── README.md              # ADR index
│   │   ├── 0001-monorepo-choice.md
│   │   └── 0002-ui-library-isolation.md
│   ├── runbooks/
│   └── diagrams/
│
├── .github/                       # CI/CD workflows, CODEOWNERS, PR templates
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── release.yml
│   └── CODEOWNERS
│
├── turbo.json                     # Task orchestration
├── pnpm-workspace.yaml            # Workspace package discovery + catalog
├── package.json                   # Root: private: true, shared scripts
└── README.md
```

---

## Key Decisions Encoded in This Structure

| Decision | Rationale |
|---|---|
| `apps/` strictly for deployables | Turborepo's official guidance: application packages are the terminal nodes of the package graph. Nothing installs them. |
| `packages/` for everything shared | All internal libraries live here regardless of technical layer. |
| `tooling/` separate from `packages/` | Build-time config is not runtime code. Mixing them confuses dependency graphs. |
| `infra/` at root level | Infrastructure code has a different change rate and owner than application code. |
| `docs/adr/` in-repo | ADRs must be version-controlled alongside the code they describe. |
| `CODEOWNERS` in `.github/` | Prevents ownership decay at scale. Every major package should be owned by a team. |

---

## pnpm Workspace Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tooling/*"

catalog:
  react: "^19.0.0"
  typescript: "^5.5.0"
  vitest: "^2.0.0"
  # All shared dependency versions live here, not in individual package.json files
```

## Root package.json

```json
{
  "name": "my-platform",
  "private": true,
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "test": "turbo test",
    "check-types": "turbo check-types"
  },
  "devDependencies": {
    "turbo": "latest"
  },
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=9.0.0"
  }
}
```

## Individual Package package.json

```json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": {
      "import": "./src/index.ts",
      "require": "./dist/index.cjs"
    }
  },
  "devDependencies": {
    "@repo/typescript-config": "workspace:*",
    "typescript": "catalog:"
  }
}
```
