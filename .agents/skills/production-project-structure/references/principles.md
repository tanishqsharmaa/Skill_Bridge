# Architectural Principles Reference (P1–P10)

> Source: Synthesized from Turborepo official docs, Nx documentation, Feature-Sliced Design,
> Domain-Driven Design (Evans), Clean Architecture (Martin), Hexagonal Architecture (Cockburn),
> and senior engineering blogs from Vercel, Nx team, ELEKS, DSI Innovators, ZestMinds (2025–2026).

These 10 principles apply regardless of stack, language, or team size. They are the "why" behind every structural recommendation.

---

## P1 — Single Responsibility at Every Level

Every folder, module, and package should have one reason to change. If you struggle to write a one-sentence description of a folder's purpose, it needs to be split or renamed.

**Application:** If `packages/shared/` exports UI primitives, API types, authentication helpers, and database utilities — it violates this principle. Split it.

---

## P2 — Explicit Boundaries, Not Implicit Trust

Modules expose a public API surface (an `index.ts`, `__init__.py`, or `mod.rs`). Internal implementation files are not importable by external consumers. Nx module boundary lint rules and pnpm strict hoisting enforce this mechanically.

**Why this matters:** Implicit filesystem access creates invisible coupling. When you refactor an internal file path, every consumer that imported it directly breaks silently.

**Correct:**
```typescript
import { UserCard } from '@repo/ui';
```

**Wrong:**
```typescript
import { UserCard } from '@repo/ui/src/user-card/UserCard';
```

---

## P3 — Dependency Inversion at the Package Level

Infrastructure adapters (databases, HTTP clients, queues) depend on domain interfaces — not the other way around. The domain never imports a framework. This is the core of both Clean Architecture and Hexagonal Architecture.

**Dependency arrows point inward:**
```
Presentation → Application → Domain ← Infrastructure
```

**Domain imports:** Only other domain code and pure utilities.  
**Infrastructure imports:** Domain interfaces (to implement them), never the other way.

---

## P4 — Co-location Is the Default

Tests, types, styles, and stories that belong to a module should live next to it, not in a separate top-level tree.

**Exception:** E2E/integration tests that span modules go in a dedicated top-level `tests/` directory.

**Why:** When code and its tests live in different top-level directories, adding a new feature requires jumping between two unrelated trees. Co-location makes the codebase navigable.

---

## P5 — Stable Public APIs vs. Volatile Internals

The fewer files that are part of a module's public API, the easier refactoring becomes. Every file in `src/` that is not re-exported from the barrel is a private implementation detail and may change freely.

**Goal:** Public API surface = only what's in `index.ts`. Everything else is an implementation detail.

---

## P6 — Structure Grows Incrementally

Do not impose the structure of a 50-engineer team on a 3-engineer project. Start with the simplest honest structure (a flat feature list inside a single app), and extract shared packages only when two or more consumers exist.

**Common mistake:** Creating `packages/ui`, `packages/utils`, `packages/types` on day 1 for a project with a single app. These packages have one consumer and their APIs are locked in before requirements are understood.

---

## P7 — Naming Encodes Intent

The folder name is the first line of documentation. Prefer `user-authentication/` over `auth/`, `payment-gateway-adapter/` over `payments/`. Prefer `kebab-case` for directory names universally. Use `@scope/package-name` for internal npm package names.

**Test:** Would a new team member understand the purpose of this folder without opening a file? If yes, the name is good.

---

## P8 — Ownership Must Be Codified

CODEOWNERS files in monorepos prevent the "tragedy of the commons." Every directory above `src/` should map to at least one owning team or individual. Without this, shared packages become orphaned over time.

**Symptom of missing ownership:** A shared package that "everyone owns" gets changed by someone who doesn't understand all its consumers, breaking multiple apps at once.

---

## P9 — Boundaries Must Be Mechanically Enforced

Conventions alone do not survive team growth. Use ESLint `@nx/enforce-module-boundaries`, pnpm's strict hoisting, `dependency-cruiser`, or `arch-unit` to make boundary violations a build failure, not a code review comment.

**The rule of thumb:** If a boundary violation can only be caught in code review, it will eventually be missed. If it's a build failure, it cannot ship.

---

## P10 — Configuration Is Infrastructure

Shared TypeScript configs, ESLint configs, and Prettier configs are packages — versioned and governed like any other package. Do not copy-paste them across workspaces.

**Why:** Copy-pasted configs diverge silently over time. A shared `@repo/typescript-config` package ensures one upgrade updates all packages simultaneously.
