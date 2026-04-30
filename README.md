# sellier

Scaffold a Claude Code agent harness into any project.

A **harness** is the system that lets an AI coding agent produce correct, high-quality code consistently. It is four things working together:

1. **Guidance** — `CLAUDE.md` and rules in `.claude/rules/` that shape what the agent writes.
2. **Guardrails** — automated checks (lint, tests, type-checking) wrapped in commands the agent runs.
3. **Flywheel** — a feedback loop: review feedback updates a rule file, reloads it, and re-applies. Every review improves every future conversation.
4. **Executable Workflows** — agents, commands, and skills under `.claude/` that turn institutional knowledge into runnable procedures.

`sellier` ships a generic, slim version of all four. You run it once in your project, then run a single Claude command (`/saddle-up`) to fill in placeholders with project specifics.

Read the [blog post](https://dev.to/tacoda/building-a-harness-how-we-standardized-agentic-coding-in-a-real-codebase-4oab) that inspired this tool.

## Quick start

Four steps from zero to a project-aware harness:

```
# 1. Install
pip install sellier

# 2. Scaffold the harness into your project
cd /path/to/your/project
sellier init
```

Then open the project in Claude Code and run:

```
# 3. Customize the harness for this project
/saddle-up

# 4. Audit the codebase against the harness standards
/giddy-up
```

`/saddle-up` reads your repo (package files, build config, README, branch state) and proposes values for every `[PLACEHOLDER]` in the harness. You confirm or correct, and Claude rewrites the files.

`/giddy-up` walks the codebase looking for violations of the rules in `.claude/rules/` and reports findings in a single table. It is read-only — you decide what to fix.

---

## What `sellier init` writes

```
CLAUDE.md
.claude/
├── settings.json
├── agents/
│   ├── ci-diagnose.md
│   ├── refactor-changes.md
│   ├── review-functional.md
│   ├── review-security.md
│   └── self-review.md
├── commands/
│   ├── giddy-up.md
│   ├── pre-commit.md
│   └── saddle-up.md
├── rules/
│   ├── commits.md
│   ├── design-principles.md
│   ├── security.md
│   └── tests.md
└── skills/
    └── implement-change/SKILL.md
```

## CLI reference

```
sellier init [PATH]    # default: current directory
                       #   --force, -f   overwrite existing harness files in place
                       #   --clean       remove existing .claude/ before writing
sellier version        # print installed version
sellier --help
```

### Alternative installs

```
uv tool install sellier         # if you use uv
pipx install sellier            # isolated install via pipx
```

### Placeholder syntax

Every project-specific value in the harness is a `[PLACEHOLDER]` token — uppercase letters, digits, and underscores in square brackets. The `/saddle-up` command grep-finds and replaces them. Common placeholders:

| Token | Example value |
|---|---|
| `[PROJECT_NAME]` | "Acme Portal" |
| `[PROJECT_DESCRIPTION]` | "Internal billing dashboard for Acme accounts" |
| `[TECH_STACK]` | "TypeScript, Next.js 15, Prisma, PostgreSQL" |
| `[MAIN_BRANCH]` | "main" |
| `[TASK_TRACKER]` | "Linear" |
| `[CI_PROVIDER]` | "GitHub Actions" |
| `[LINT_COMMAND]` | "pnpm lint" |
| `[TEST_COMMAND]` | "pnpm test" |
| `[FRONTEND_TEST_COMMAND]` | "pnpm test:ui" |
| `[BUILD_COMMAND]` | "pnpm build" |

You can edit the harness afterwards. `sellier` writes; it does not own the files - _you_ do.

---

## For developers

### Stack

- Python 3.14
- [uv](https://github.com/astral-sh/uv) for environments and packaging
- [typer](https://typer.tiangolo.com/) for the CLI
- [pytest](https://docs.pytest.org/) for tests
- [hatchling](https://hatch.pypa.io/) as the build backend

### Layout

```
src/sellier/
├── __init__.py          # version
├── cli.py               # typer app — init / version
├── scaffolder.py        # template traversal and copy logic
└── templates/           # the harness, shipped as package data
    ├── CLAUDE.md
    └── .claude/...
tests/
├── test_cli.py          # typer CliRunner tests
└── test_scaffolder.py   # scaffolder logic tests
```

The templates directory **is** the deliverable. `cli.py` and `scaffolder.py` are thin — most of the value is in the markdown.

### Develop

```
uv sync              # install runtime + dev dependencies
uv run pytest        # run tests
uv run sellier init /tmp/sellier-smoke   # local smoke test
```

### Adding a placeholder

1. Use `[NEW_PLACEHOLDER]` in the relevant template file.
2. Add a row to the placeholder table in this README.
3. Add an entry to the expected-placeholders list in `.claude/commands/saddle-up.md` so Claude knows to look for it.

### Adding a rule, agent, command, or skill

Drop a new file under `src/sellier/templates/.claude/{rules,agents,commands,skills}/`. It will ship on the next release. Use placeholders for any project-specific text.

### Tests

```
uv run pytest                              # all tests
uv run pytest tests/test_scaffolder.py     # one file
uv run pytest -k init                      # one keyword
```

The scaffolder tests assert byte-equality between the templates shipped in the package and what `init` writes — if you add a binary asset, the test still applies.

### Release

Bump the version in `pyproject.toml` and `src/sellier/__init__.py` together in a single `chore(release):` commit, then:

```
uv build
uv publish
```

---

## License

MIT
