# Spec Driven Development

## Overview

Spec Driven Development is a development approach where the specification of the desired behavior is the primary input to the development process. This approach is often used in the context of software development to ensure that the final product meets the needs of the end user.

## 1) Minimal setup (files + tiny examples)

```
/specs/
  requirements.md
  design.md
  tasks.md
/commands/
  ingest.md
  design.md
  plan.md
  implement.md
  test.md
README.md
```

### /specs/requirements.md (EARS-style, tiniest possible)

```markdown
# Requirements

## R1 – Hello endpoint
Ubiquitous: The **hello service** shall return the string "Hello, Spec!" when invoked.

Event-driven: When the user calls `/hello`, the **hello service** shall respond `200 OK` with body `"Hello, Spec!"`.

Quality: The response shall be returned in <50 ms on localhost.
```

### /specs/design.md

```markdown
# Design
- Runtime: Python 3.x + FastAPI (or plain CLI if you prefer)
- Endpoint: GET /hello -> returns text/plain "Hello, Spec!"
- Files: app/main.py, tests/test_hello.py
```

### /specs/tasks.md

```markdown
# Tasks
- [ ] Scaffold project structure
- [ ] Implement /hello
- [ ] Add test for /hello
- [ ] Run tests locally
```

## 2) Steps we’ll follow (KISS)

	1.	Ingest specs → create/validate requirements.md.  ￼
	2.	Design → produce design.md from requirements.  ￼
	3.	Plan → expand to tasks.md with a short, checkable list.  ￼
	4.	Implement → write minimal code + tests per tasks.  ￼
	5.	Test & Review → run tests; refine specs if needed.

## 3) The loop (use these command cards as you iterate)

### A) /ingest

- **What it does:** Creates or normalizes requirements.md using EARS.
- **Expect after run:** specs/requirements.md (valid, minimal).

### B) /design

- **What it does:** Translates requirements → a tiny design doc with filenames.
- **Expect after run:** specs/design.md updated.

### C) /plan

- **What it does:** Generates a short, executable checklist.
- **Expect after run:** specs/tasks.md.

### D) /implement

- **What it does:** Writes minimal code + tests so we have a runnable “hello world.”
- **Expect after run (FastAPI option):**
	- app/main.py
	- tests/test_hello.py
	- pyproject.toml (or requirements.txt)
	- README.md (1-liner run instructions)

### E) /test

- **What it does:** Runs tests, reports results; if failing, proposes concrete edits.
- **Expect after run:** Test output; possibly a patch diff proposal.

### F) /review

- **What it does:** Compares requirements.md ↔ code/tests; suggests next tasks.
- **Expect after run:** Updated specs/tasks.md with follow-ups (docs, perf, etc.).
