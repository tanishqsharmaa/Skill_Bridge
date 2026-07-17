# Naming Conventions Reference

> Source: Turborepo official docs, Nx team conventions, Feature-Sliced Design documentation,
> Python PEP 8, Go naming conventions, and industry-wide best practices (2025–2026).

These naming conventions apply across all stacks unless a specific override is noted.

---

## Directory Names

| Context | Convention | Examples | Notes |
|---|---|---|---|
| All directories | `kebab-case` | `user-authentication/`, `payment-gateway/` | Universal across all stacks |
| Feature directories | Descriptive nouns | `user-profile/`, `order-management/` | Avoid abbreviations |
| Domain directories | Business capability name | `billing/`, `notifications/`, `users/` | Matches bounded context |
| Infrastructure directories | Technical purpose | `persistence/`, `messaging/`, `http/` | Only inside `infrastructure/` |

---

## Package Names (Internal npm Packages)

| Context | Convention | Examples |
|---|---|---|
| Internal packages | `@scope/kebab-case` | `@repo/ui`, `@repo/typescript-config` |
| Tooling packages | `@scope/tool-name` | `@repo/eslint-config`, `@repo/prettier-config` |
| Published packages | `@org/package-name` | `@mycompany/design-system` |

**The scope `@repo` is the Turborepo convention for internal packages.** Your org's actual scope
can differ, but keep it consistent across the entire monorepo.

---

## TypeScript / JavaScript Files

| Context | Convention | Examples |
|---|---|---|
| Utility functions | `camelCase.ts` | `userService.ts`, `formatDate.ts` |
| React components | `PascalCase.tsx` | `UserCard.tsx`, `LoginForm.tsx` |
| API route files | `route.ts` | `route.ts` (Next.js App Router convention) |
| Test files | Same name + `.test.ts` or `.spec.ts` | `userService.test.ts` |
| Type definition files | `camelCase.types.ts` or `types.ts` | `user.types.ts` |
| Constants | `SCREAMING_SNAKE_CASE` for values | `const MAX_RETRIES = 3` |

---

## Python Files

| Context | Convention | Examples |
|---|---|---|
| Module files | `snake_case.py` | `user_service.py`, `order_repository.py` |
| Class names | `PascalCase` | `UserService`, `OrderRepository` |
| Function names | `snake_case` | `get_user_by_id()`, `create_order()` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT = 3` |
| Private functions | `_leading_underscore` | `_validate_input()` |

---

## Architecture Decision Records (ADRs)

| Context | Convention | Examples |
|---|---|---|
| ADR files | `NNNN-imperative-title.md` | `0001-adopt-turborepo.md` |
| ADR numbering | Sequential, zero-padded to 4 digits | `0001`, `0002`, `0015` |
| ADR title style | Imperative verb phrase | `adopt-qdrant-as-vector-db`, `migrate-to-pnpm-workspaces` |
| ADR status | `Proposed` → `Accepted` → `Deprecated` or `Superseded by #NNNN` | — |

**ADR template:**
```markdown
# NNNN — Adopt Turborepo for Monorepo Orchestration

## Status
Accepted

## Context
[Why this decision was needed]

## Decision
[What was decided and why]

## Consequences
[What becomes easier, what becomes harder]
```

---

## Configuration Files

| File | Location | Notes |
|---|---|---|
| `.env.local` | App root | Local development overrides (gitignored) |
| `.env.staging` | App root | Staging environment |
| `.env.production` | App root | Production environment (secrets via CI) |
| `Dockerfile` | Service root | One per deployable service |
| `docker-compose.yml` | Repo root or service root | For local development |
| `ci.yml`, `release.yml` | `.github/workflows/` | CI/CD workflows |
| `CODEOWNERS` | `.github/` | Ownership definitions |
| `turbo.json` | Repo root | Task orchestration |
| `pnpm-workspace.yaml` | Repo root | Workspace discovery |
| `tsconfig.json` | Per package | Extends `@repo/typescript-config` |

---

## Go Naming

| Context | Convention | Examples |
|---|---|---|
| Package names | Short, lowercase, no underscores | `user`, `order`, `http` |
| Interface names | Describes behavior, often `-er` suffix | `UserRepository`, `OrderService` |
| Exported identifiers | `PascalCase` | `GetUser()`, `CreateOrder()` |
| Unexported identifiers | `camelCase` | `validateInput()`, `parseResponse()` |
| Test files | Same name + `_test.go` | `user_repository_test.go` |

---

## Common Mistakes to Avoid

| Bad | Better | Why |
|---|---|---|
| `auth/` | `user-authentication/` | Too abbreviated — unclear scope |
| `payments/` | `payment-gateway-adapter/` | Unclear if it's domain or infra |
| `helpers/` | `utils/` or move to domain | "Helpers" has no meaning |
| `common/` | Split by purpose | Vague — leads to AP2 |
| `MyComponent.js` | `MyComponent.tsx` | Missing type annotation for TS |
| `index.js` (everything) | Named exports + barrel | Makes tree-shaking impossible |
