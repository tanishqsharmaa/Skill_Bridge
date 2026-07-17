# Tooling Configurations Reference

> Ready-to-use configuration file content for monorepo tooling.
> Copy-paste these into your project, then customize.

---

## turbo.json (Turborepo Task Orchestration)

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "check-types": {
      "dependsOn": ["^check-types"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "persistent": true,
      "cache": false
    }
  }
}
```

**Key patterns:**
- `"dependsOn": ["^build"]` — runs after all dependency packages have been built
- `"persistent": true` — long-running dev servers (don't cache)
- `"outputs"` — what to cache (omit for lint/type-check since they produce no artifacts)

---

## pnpm-workspace.yaml

```yaml
packages:
  - "apps/*"
  - "packages/*"
  - "tooling/*"

catalog:
  # Pin shared dependency versions here — reference with "catalog:" in package.json
  react: "^19.0.0"
  react-dom: "^19.0.0"
  "@types/react": "^19.0.0"
  typescript: "^5.5.0"
  vitest: "^2.0.0"
  eslint: "^9.0.0"
  prettier: "^3.0.0"
  tailwindcss: "^4.0.0"
```

**Usage in individual package.json:**
```json
{
  "dependencies": {
    "react": "catalog:",
    "react-dom": "catalog:"
  },
  "devDependencies": {
    "typescript": "catalog:",
    "vitest": "catalog:"
  }
}
```

---

## TypeScript Config (tooling/typescript-config/)

### base.json
```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "esModuleInterop": true,
    "incremental": false,
    "isolatedModules": true,
    "lib": ["es2022"],
    "module": "NodeNext",
    "moduleDetection": "force",
    "moduleResolution": "NodeNext",
    "noUncheckedIndexedAccess": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "strict": true,
    "target": "ES2022"
  }
}
```

### nextjs.json
```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "noEmit": true,
    "plugins": [{ "name": "next" }],
    "target": "ES2017"
  }
}
```

### Usage in a package
```json
{
  "extends": "@repo/typescript-config/base.json",
  "include": ["src"],
  "exclude": ["node_modules"]
}
```

---

## ESLint Config (tooling/eslint-config/)

### Nx Module Boundary Rules (.eslintrc.json in workspace root)

```json
{
  "root": true,
  "plugins": ["@nx"],
  "rules": {
    "@nx/enforce-module-boundaries": [
      "error",
      {
        "enforceBuildableLibDependency": true,
        "allow": [],
        "depConstraints": [
          {
            "sourceTag": "type:feature",
            "onlyDependOnLibsWithTags": ["type:feature", "type:ui", "type:data-access", "type:util"]
          },
          {
            "sourceTag": "type:ui",
            "onlyDependOnLibsWithTags": ["type:ui", "type:util"]
          },
          {
            "sourceTag": "type:data-access",
            "onlyDependOnLibsWithTags": ["type:data-access", "type:util"]
          },
          {
            "sourceTag": "type:util",
            "onlyDependOnLibsWithTags": ["type:util"]
          },
          {
            "sourceTag": "scope:users",
            "onlyDependOnLibsWithTags": ["scope:users", "scope:shared"]
          },
          {
            "sourceTag": "scope:orders",
            "onlyDependOnLibsWithTags": ["scope:orders", "scope:shared"]
          }
        ]
      }
    ]
  }
}
```

---

## dependency-cruiser Configuration (.dependency-cruiser.js)

For projects using dependency-cruiser (Turborepo or non-Nx monorepos):

```javascript
module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      comment: "Circular dependencies are unconditionally forbidden.",
      from: {},
      to: {
        circular: true
      }
    },
    {
      name: "no-cross-feature-imports",
      severity: "error",
      comment: "Features must not import from each other. Extract to shared/ instead.",
      from: {
        path: "^src/features/([^/]+)/"
      },
      to: {
        path: "^src/features/([^/]+)/",
        pathNot: "^src/features/$1/"  // same feature is OK
      }
    },
    {
      name: "domain-no-framework-imports",
      severity: "error",
      comment: "Domain layer must not import framework libraries.",
      from: {
        path: "^src/domain/"
      },
      to: {
        path: "^(react|next|fastapi|sqlalchemy|langchain)"
      }
    }
  ],
  options: {
    doNotFollow: {
      path: "node_modules"
    },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: "tsconfig.json" }
  }
};
```

---

## CODEOWNERS Template (.github/CODEOWNERS)

```
# Global fallback — platform team reviews everything not explicitly assigned
*                               @my-org/platform-team

# Apps
apps/web/                       @my-org/frontend-team
apps/api/                       @my-org/backend-team
apps/admin/                     @my-org/admin-team

# Shared packages — platform team owns these
packages/ui/                    @my-org/design-system-team
packages/types/                 @my-org/platform-team
packages/utils/                 @my-org/platform-team

# Infrastructure — separate ownership
infra/                          @my-org/devops-team
.github/                        @my-org/platform-team

# Docs — tech lead is accountable
docs/adr/                       @my-org/tech-leads
```

---

## GitHub Actions CI Template (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize]

jobs:
  build:
    name: Build and Test
    timeout-minutes: 15
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Get pnpm store directory
        id: pnpm-cache
        shell: bash
        run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

      - name: Setup pnpm cache
        uses: actions/cache@v4
        with:
          path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
          key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-pnpm-store-

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build
        run: pnpm build

      - name: Lint
        run: pnpm lint

      - name: Type check
        run: pnpm check-types

      - name: Test
        run: pnpm test
```

---

## pyproject.toml (Python — FastAPI or AI/RAG)

```toml
[project]
name = "my-service"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.8.0",
    "pydantic-settings>=2.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[tool.ruff]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
