# AGENTS.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Project Directory Planning
**Define the project directory structure and how to use it**

This section tells the agent *where* to document its work and *how* each file
should be maintained as the project progresses. Every file below lives under
`documentation/` at the project root.

**Why this structure exists:** each file has one clear, narrow purpose so the
agent never has to read the entire codebase or every doc to find something.
Instead, it goes straight to the specific file that matches the task at hand
(e.g. a past error → `error_log.md` only, current file layout →
`project_map.md` only, this sprint's tasks → `sprint_plan/sprintNN.md` only).
Pinpoint reads, not full scans.

### 📁 documentation/

| Path                                   | Purpose                                                                                                   | How the agent should use it                                                                                                     |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `project_idea.md`                       | Idea & vision doc — problem statement, elevator pitch, solution concept, goals, external alignment.        | Read-only reference. Only edit if the core vision/scope changes.                                                                  |
| `project_structure.md`                  | Codebase blueprint — planned folder/file tree, module boundaries, naming conventions, stack-to-dir mapping.| Written once during planning. Update only when the *intended* architecture changes.                                              |
| `system_design.md`                      | Technical architecture — capacity estimates, data flow, API contracts, infra decisions, component interactions. | Reference during implementation; update when architecture decisions evolve.                                                       |
| `system_design_doc.md`                  | Formal/polished write-up of the system design for review or submission.                                    | Generate/update near milestones or before a review — not a working file.                                                          |
| `project_map.md`                        | **Live** copy of the actual project structure, used to track real files as they're created/moved/removed.  | Update every time a file or folder is added, deleted, or renamed, so it always mirrors the real repo state (not the plan).        |
| `error_log.md`                          | Log of every error encountered and how it was resolved.                                                    | Append an entry each time a bug/error is hit and fixed: what happened, root cause, fix applied. Never delete past entries.         |
| `sprint_tracker.md`                     | Tracks overall sprint progress.                                                                            | Update at the start/end of each sprint and after major tasks — mark items pending / in-progress / done / blocked.                 |
| `plan/implementation_plan.md`           | Master execution roadmap — ordered, time-boxed build plan broken into sprints/phases with tasks and success criteria. | Read before starting any new sprint. This is the source of truth the sprint files are derived from.                              |
| `sprint_plan/`                          | One file per sprint, holding that sprint's detailed task breakdown.                                        | Before starting a sprint, create `sprint_plan/sprintNN.md` (e.g. `sprint01.md`, `sprint02.md`...) derived from `implementation_plan.md`. |

### Agent working rules
- Read with pinpoint accuracy: open only the specific file relevant to the current task — never scan the whole `documentation/` folder or codebase "just in case."
- Before starting any task: check `project_map.md` and `sprint_tracker.md` to know current state.
- Before starting a sprint: create/open `sprint_plan/sprintNN.md`, scoped from `plan/implementation_plan.md`.
- Immediately after fixing any bug: append to `error_log.md`.
- At the end of each work session or sprint: update `sprint_tracker.md`.
- Whenever the file/folder structure changes: update `project_map.md` (do not touch `project_structure.md`, which is the original plan, not the live state).


## 6. Build Folder
**Always use the `build/` folder at root to build and scaffold the project**
 
All actual project code — source files, scaffolding, generated boilerplate,
installed dependencies, build artifacts — goes inside `build/` at the project
root. `documentation/` never holds code; `build/` never holds planning docs.
This keeps docs and implementation cleanly separated and lets `project_map.md`
track one unambiguous location for the real codebase.
 
### Agent working rules
- Scaffold and build the project only inside `build/` — never at the repo root and never inside `documentation/`.
- Before scaffolding, check `project_structure.md` for the intended layout and mirror it inside `build/`.
- After scaffolding or adding new files/folders inside `build/`, update `project_map.md` to reflect the change.
- If `build/` doesn't exist yet, create it before generating any project code.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## 7. Command Execution Policy
**Never auto-run long commands. Hand them off and wait for feedback.**

### Auto-run (agent executes directly)
These are fast, safe, and non-destructive — run them without asking:
- Creating files and directories (`New-Item`, `mkdir`)
- Reading file contents (`Get-Content`, `cat`)
- Listing directory structure (`Get-ChildItem`, `ls`)
- Short validation scripts (e.g. `python -c "import foo; print('OK')"`)
- Counting lines in a file

### Hand-off (agent prints the command — user runs it and reports back)
These are long-running, install packages, modify the environment, or interact with external services — **always print the command and wait for the user to run it and report back**:

| Category | Examples |
|----------|---------|
| Package installation | `pip install`, `npm install`, `uv pip install` |
| Test suites | `pytest`, `npm test`, `vitest` |
| Build / compile | `npm run build`, `modal deploy`, `docker build` |
| Database operations | `python scripts/embed_job_skills.py`, SQL migrations |
| Dev servers | `uvicorn`, `npm run dev`, `modal serve` |
| Git operations | `git push`, `git pull`, `git merge` |
| Any command expected to run > 5 seconds | — |

### How to hand off
Present the command in a clear code block with the working directory, like:

```
Run this in Build/backend/ (with virt activated):

    F:\IBM internship\sunmission\Project\Build\backend\virt\Scripts\activate
    python -m pytest tests/integration/test_db_connection.py -v

Then paste the output back so I can review results.
```

### Virtual environment
The project uses a single virtual environment at the fixed path below. Always use this virt for any Python command — never the system Python.

```
F:\IBM internship\sunmission\Project\Build\backend\virt\
```

- **Activate (PowerShell):** `F:\IBM internship\sunmission\Project\Build\backend\virt\Scripts\activate`
- **Python binary:** `F:\IBM internship\sunmission\Project\Build\backend\virt\Scripts\python.exe`
- **Pip binary:** `F:\IBM internship\sunmission\Project\Build\backend\virt\Scripts\pip.exe`

### Agent working rules
- If in doubt whether a command is "short" or "long", hand it off.
- Never chain a long command after a short one in the same `run_command` call.
- After the user reports back output, act on it immediately — don't ask them to re-run.

---

## 8. Git Commit & Push After Every Interaction

**At the end of every interaction where any file was created or modified, always hand off a git commit + push.**

### When to trigger
- Any time one or more files were written, edited, or deleted during the interaction.
- Always at the end of the response — never skip it, even for small changes.

### Commit message format
```
<type>(<scope>): <short summary>

<optional bullet list of what changed>
```

Types: `feat` · `fix` · `docs` · `chore` · `test`  
Scope: sprint number or module (e.g. `sprint1`, `config`, `schema`, `agents`)

### How to hand off
Always end the response with this block:

```
📋 Commit & push — run from the project root:

    git add .
    git commit -m "type(scope): summary"
    git push

```

### Agent working rules
- Write the commit message — don't make the user think of one.
- Always use `git add .` from the repo root so nothing is missed.
- `git push` is always included — a local-only commit is not enough.
- If the interaction had no file changes (e.g. pure Q&A), skip this rule silently.