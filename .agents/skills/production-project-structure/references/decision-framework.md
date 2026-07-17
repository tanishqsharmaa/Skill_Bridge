# Decision Framework — Choosing the Right Structure

> Source: Synthesis from Turborepo official docs, Nx team blog, Feature-Sliced Design documentation,
> and engineering blogs from mature product organizations (2025–2026).

Use this 5-step framework when a user doesn't know which structure to choose, or when they're
starting a new project and need to make foundational decisions.

---

## Overview

```
Step 1 → Assess team and scale
Step 2 → Choose organizational axis (feature-first vs. layer-first)
Step 3 → Define module boundaries before writing code
Step 4 → Choose enforcement mechanism
Step 5 → Plan the evolution path
```

---

## Step 1 — Assess Team and Scale

| Team size | Initial structure recommendation |
|---|---|
| 1–3 devs, 1 domain | Single-package with domain-based internal folders. No monorepo needed. |
| 3–10 devs, 1–3 apps | Monorepo with `apps/` + `packages/`. Turborepo + pnpm. |
| 10–50 devs, multiple teams | Monorepo with enforced module boundaries (Nx tags or dependency-cruiser). CODEOWNERS mandatory. |
| 50+ devs, platform ownership | Consider Nx with polygraph or Bazel for polyglot. Platform team owns shared packages. |

**Key insight:** The number of *teams* matters more than the number of engineers. If two separate
teams own different parts of the codebase, you need enforced boundaries regardless of total headcount.

---

## Step 2 — Choose Organizational Axis

### Choose Feature-First When:
- Multiple business domains exist (users, orders, billing, notifications, etc.)
- Different teams own different features
- Features are deployed or extracted independently over time
- You expect to grow past 10 engineers

### Choose Layer-First When:
- Single domain, simple CRUD application
- Small team (under 5 devs) with full-stack ownership
- Prototype or internal tool with short expected lifespan

### Hybrid (Recommended for Medium/Large):
Feature-first at the top level, consistent layer structure inside each feature.

**Example (FastAPI):**
```
# Feature-first at top level:
users/
  router.py       ← layer inside feature
  service.py      ← layer inside feature
  repository.py   ← layer inside feature
  schemas.py      ← layer inside feature
orders/
  router.py
  service.py
  ...
```

**Why hybrid wins:** You get the navigability of feature-first (find `users/` immediately) with
the consistency of layer-first (always know where the business logic lives within a feature).

---

## Step 3 — Define Module Boundaries Before Writing Code

Answer these three questions:

1. **Which modules will change together?** (They should be co-located.)
2. **Which modules will change independently?** (They should be separate packages.)
3. **Which modules are consumed by multiple others?** (They should have an explicit public API.)

**For JS/TS monorepos:** Define the package topology before writing code.
- `packages/ui` — design system, consumed by `apps/web` and `apps/admin`
- `packages/types` — shared DTOs, consumed by `apps/web` and `apps/api`
- `packages/utils` — pure utilities, consumed by all packages

**For Python projects:** Define which modules can import from which others.
- `core/` imports from nothing (or only stdlib)
- `domain/` imports from `core/` only
- `infrastructure/` imports from `domain/` interfaces
- `presentation/` imports from `application/` only

---

## Step 4 — Choose Enforcement Mechanism

| Mechanism | Tooling | When to use |
|---|---|---|
| Package-level boundary enforcement | pnpm strict hoisting, `workspace:*` protocol | Always, in JS/TS monorepos |
| Import path enforcement | Nx `@nx/enforce-module-boundaries`, `dependency-cruiser` | Teams > 5 engineers |
| Type boundary enforcement | TypeScript `paths` in tsconfig | When using TypeScript |
| Ownership enforcement | GitHub CODEOWNERS | Teams > 10 engineers |
| Test coverage enforcement | Vitest / Jest coverage thresholds in CI | When coverage matters |
| Architectural compliance | `arch-unit` (Java/JVM), `pylint` with custom rules (Python) | Strict enterprise environments |

**The principle:** If a boundary violation can only be caught in code review, it will eventually
be missed. If it's a build failure, it cannot ship. Move enforcement left, toward the developer.

---

## Step 5 — Plan the Evolution Path

Plan your growth trajectory upfront. Structure decisions made at step 1 constrain what's possible at step 3.

### Small → Medium
Extract shared `ui` and `utils` packages when two apps share components.
Signal: You're copy-pasting a component from `apps/web` into `apps/admin`.

### Medium → Large
Extract domain packages. Introduce CODEOWNERS. Add module boundary lint rules.
Signal: A change in `packages/ui` breaks `apps/admin` in unexpected ways.

### Large → Platform
Split into platform (shared infra) and product (feature) layers. Introduce a platform team with own release cadence.
Signal: Multiple product teams are blocked on the same shared packages. A platform team should own those.

---

## Quick Decision Card

Use this when you need to give an immediate recommendation:

```
User has 1–3 engineers, single app?
  → Single-repo, flat feature structure, no monorepo tooling yet

User has 3–10 engineers, multiple apps sharing code?
  → Turborepo + pnpm monorepo, apps/ + packages/ + tooling/ structure

User has 10+ engineers or multiple teams?
  → Add Nx module boundaries or dependency-cruiser, CODEOWNERS mandatory

User has AI/ML components?
  → Separate prompts/, retrieval/, agents/ even in a small project — these grow fast

User is building a published library?
  → Single package, strict public API (index.ts only), ESM + CJS dual build
```
