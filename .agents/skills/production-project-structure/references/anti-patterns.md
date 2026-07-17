# Anti-Patterns Reference

> Source: Synthesized from multiple independent sources including Foote & Yoder (1997) "Big Ball of Mud",
> Turborepo official docs, Nx team blog, DSI Innovators, ZestMinds, auth0.com, TechTarget (2025–2026).
>
> These are structural mistakes documented across multiple sources.
> Presented in order of severity — AP1 is the most destructive, AP10 is the most subtle.

---

## AP1 — The Big Ball of Mud *(Severity: Critical)*

**Symptom:** No discernible structure. Files added wherever felt convenient. No clear separation between business logic and infrastructure. Every module imports every other module.

**Cause:** Deadline pressure, no architectural governance, high team turnover.

**Cost:** Exponentially increasing time to add features. Untestable code. Impossible to extract modules for reuse. First documented in Foote & Yoder (1997); still the most common failure mode.

**Fix:** Start with feature-based restructuring. Pick one domain (e.g., `users/`) and fully reorganize it first. Prove the pattern works, then migrate domain by domain. Do not attempt a big-bang rewrite.

---

## AP2 — The Bloated Utils Folder *(Severity: High)*

**Symptom:** A `utils/`, `helpers/`, or `common/` folder that contains unrelated code: formatters, authentication logic, database helpers, API clients, and UI components all in one place.

**Cause:** Developers cannot find the right place for code, so they drop it in `utils/`.

**Cost:** The `utils/` folder becomes a garbage collection for homeless code, making it impossible to understand what any individual file does.

**Fix:** A `util` module should contain only pure, framework-free functions. Everything else belongs in its proper domain module. Run a dependency analysis on your `utils/` — anything with imports beyond `node_modules` and standard library is misplaced.

---

## AP3 — Layer-First at Scale (The Type-Based Flat Structure) *(Severity: High)*

**Symptom:** `controllers/`, `services/`, `repositories/`, `models/` folders, each containing dozens of unrelated files named after every domain object.

**Cause:** Appropriate for small projects; not refactored as the project grew.

**Cost:** Adding a feature requires touching five separate top-level folders. Conceptual cohesion of a feature is zero. Scales to approximately 10 domains before becoming unnavigable.

**Fix:** Migrate to feature-first organization. Group by `users/`, `orders/`, `billing/` etc., and keep the layer structure *inside* each feature folder. This is the hybrid pattern that scales.

---

## AP4 — Circular Dependencies *(Severity: High)*

**Symptom:** Package A imports from Package B, which imports from Package A. Tooling (Webpack, TypeScript, Python) either silently fails or produces cryptic errors.

**Cause:** Incremental coupling without architectural oversight. Common when splitting a monolith into packages without analyzing the dependency graph.

**Fix:** Introduce a third package that both A and B can depend on (a shared types or utils package). Enforce with `dependency-cruiser` or Nx's lint rules. Never treat circular deps as "acceptable technical debt" — they compound.

---

## AP5 — God Package / God Module *(Severity: High)*

**Symptom:** One package (`@repo/shared`, `core/`, `common/`) that every other package imports and that changes constantly.

**Cost:** A change to the god package invalidates the cache for the entire repository. CI rebuilds everything. The `turbo query` command for packages with more than 10 direct dependents reveals this pattern.

**Fix:** Split by function. If `@repo/shared` exports both UI primitives and API types, split it into `@repo/ui` and `@repo/types`. The cost of having 5 small packages is far lower than maintaining one giant one.

---

## AP6 — Premature Package Extraction *(Severity: Medium)*

**Symptom:** A package with a single consumer, often created speculatively ("we might need this later").

**Cost:** An internal API is locked in before requirements are understood. Refactoring requires a two-package change instead of one. Engineers working on the single consumer cannot freely refactor the API.

**Rule:** Extract when two independent consumers exist. Not before.

---

## AP7 — Nested Packages in Turborepo *(Severity: Medium)*

**Symptom:** `packages/ui/components/button/` treated as an independent package (with its own `package.json`) nested inside `packages/ui/`.

**Cause:** Turborepo explicitly does not support nested packages due to ambiguous behavior in JavaScript package managers. This produces build errors and cache poisoning.

**Fix:** Either treat the nested directory as an internal module inside the parent package, or use glob grouping (`packages/ui-*`) without nesting `package.json` files.

---

## AP8 — Hardcoded Dependency Versions Across Packages *(Severity: Medium)*

**Symptom:** React is `^18.2.0` in one package and `^19.0.0` in another. Conflicts emerge at install time. Different versions of the same library loaded at runtime, causing subtle bugs.

**Fix:** Use the pnpm `catalog:` protocol to define all shared dependency versions once in `pnpm-workspace.yaml`. Reference with `catalog:` in individual `package.json` files. This makes version upgrades a one-line change.

---

## AP9 — Tests in Production Bundles *(Severity: Low-Medium)*

**Symptom:** Test files, fixtures, and mocks are in the same source tree and accidentally shipped in production builds, increasing bundle size and exposing test data.

**Fix:** Keep unit tests co-located (using `.test.ts` or `.spec.ts` naming), but configure build tools to exclude them. Keep integration and E2E tests in a top-level `tests/` directory explicitly excluded from build outputs.

---

## AP10 — ADRs in External Wikis (Decision Amnesia) *(Severity: Low-Medium)*

**Symptom:** Architectural decisions are documented in Confluence or Notion, then rot as the system evolves without corresponding updates.

**Cost:** New team members cannot discover why a decision was made. The same debates recur every 6 months. Teams reverse decisions that were made for good reasons that were never written down.

**Fix:** ADRs live in `docs/adr/` inside the repository, versioned alongside the code. Once an ADR is "Accepted," it is immutable. A superseding decision creates a new ADR, not an edit.

---

## Using This File in an Audit

When auditing an existing codebase, structure your findings as:

```
## Audit Findings

### [Severity: High] AP3 — Layer-First at Scale
Symptom observed: The codebase has top-level controllers/, services/, models/ directories
each containing 40+ files mixing all domains.
Risk: Adding any new feature requires changes in 5 separate folders.
Recommended fix: Migrate to feature-based structure, starting with the `users` domain.
Migration effort: 2–3 days for one domain.
```

Prioritize findings by severity. High-severity findings block scaling; address them first.
