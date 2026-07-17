# SkillBridge — Error Log

Append an entry every time a bug/error is hit and fixed.
Never delete past entries.

---

## Entry 001 — 2026-07-17

**Where:** `scripts/embed_job_skills.py` — Sprint 1, Task 9

**Error:**
```
FutureWarning: All support for the `google.generativeai` package has ended.
postgrest.exceptions.APIError: {'message': 'expected 768 dimensions, not 3072'}
```

**Root cause:**
Two separate issues:
1. `google.generativeai` is deprecated — the new SDK is `google.genai`.
2. The deprecated SDK's `gemini-embedding-001` model was returning **3072 dimensions** at runtime, but the `job_skills.embedding` column was defined as `vector(768)`, causing a Postgres dimension mismatch on INSERT.

**Fix applied:**
- `embed_job_skills.py`: replaced `import google.generativeai as genai` with `from google import genai` + `from google.genai import types`. Switched `genai.configure()` → `genai.Client(api_key=...)`. Switched model from `models/gemini-embedding-001` to `text-embedding-004` (confirmed 768-dim output). Updated `embed_content()` call to new SDK shape: `client.models.embed_content(model=..., contents=..., config=types.EmbedContentConfig(...))`.
- `requirements.txt`: replaced `google-generativeai>=0.8` with `google-genai>=1.0`.

**Verification:**
Re-run `python scripts/embed_job_skills.py` — no FutureWarning, no dimension mismatch.

---

## Entry 002 — 2026-07-17

**Where:** `scripts/embed_job_skills.py` + `scripts/test_api_keys.py` — Sprint 1, Task 9

**Error:**
```
404 NOT_FOUND: models/text-embedding-004 is not found for API version v1beta,
or is not supported for embedContent.
```

**Root cause:**
`text-embedding-004` has been **retired** by Google. The current model is `gemini-embedding-001`, which defaults to **3072 dims**. Since the schema has `vector(768)`, a plain switch would cause a dimension mismatch.

**Fix applied:**
- Switched model from `text-embedding-004` → `gemini-embedding-001` in both `embed_job_skills.py` and `test_api_keys.py`.
- Added `output_dimensionality=768` to `EmbedContentConfig` — this uses the model's built-in **Matryoshka Representation Learning (MRL)** truncation to output exactly 768 dims, matching the existing `vector(768)` schema column without any schema changes.

**Verification:**
Re-run `python scripts/test_api_keys.py` — Gemini should show `PASS (dims=768)`.

---

## Entry 003 — 2026-07-17

**Where:** `scripts/embed_job_skills.py` — Sprint 1, Task 9

**Error:**
```
429 RESOURCE_EXHAUSTED: You exceeded your current quota.
Quota: EmbedContentRequestsPerMinutePerUserPerProjectPerModel-FreeTier (limit: 100)
Please retry in 31.381274072s
```

**Root cause:**
Free-tier limit is 100 embed requests/minute. With 122 rows and BATCH_SIZE=20 + 1.5s sleep, all 122 requests fired in ~10 seconds — well over the rate limit. Row 121 (`Product Manager: Agile / Scrum`) was dropped.

**Impact:** Minor — 121/122 rows inserted. SC-1 (≥100 rows) still passes ✅. The missing row is the last `Product Manager` skill.

**Fix applied:**
Added retry loop in `embed_text()`: on `429`, parses `retry in Xs` from the error message and sleeps that duration + 2s buffer before retrying. Max 3 attempts per row.

**Verification:**
121 rows already in DB — sufficient. No re-seed needed unless row 122 is specifically required.
