---
description: Diagnose a failing CI run and propose fixes (no CI is configured for sellier yet)
allowed_tools:
  - Read
  - Grep
  - Glob
  - "Bash(gh *)"
  - "Bash(git *)"
---

Diagnose the most recent failing CI run for the current branch. Read-only.

> **Note:** sellier has no CI provider configured yet. This agent is a placeholder — once CI is wired up, fill in the provider-specific commands below.

## Steps

1. Identify the most recent failed run on the current branch
2. Pull the failed job logs
3. Find the **first** failure — later failures are usually downstream
4. Map the failure back to a file or test in the diff
5. Classify: **infra** (CI machine, network, flaky), **dependency** (lockfile, version skew), or **code** (real failure)

## Output Format

- **Run URL**
- **First failing step**
- **Classification**: infra | dependency | code
- **Root cause** in one sentence
- **Proposed fix** — concrete change with file paths
- **Verification** — what command to run locally to confirm
