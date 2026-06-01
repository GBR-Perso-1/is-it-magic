# General Engineering Standards

- Windows environment — use PowerShell for scripts
- British English in all comments and documentation

## Company Context

Read `.claude/project-context.md` at session start — company, team size, user base, ownership model, release cadence. Max 100 words.

## Git

- Prefer `/repo-commit` for commits — it runs tests, applies the conventional format, and gates the push
- Conventional commits: `type(scope): description` (feat / fix / chore / refactor) — applies to direct commits too
- Main: no PR needed — commits may span multiple concerns
- Branch/PR: one feature or fix per branch
- PR titles match commit convention
- Never push to remote without user confirmation

## Offline Auth Bypass

- **Never** toggle `OfflineAuthBypass` or `VITE_APP_OFFLINE_AUTH_BYPASS` — developer-only, do not touch

## Dependencies — No Global Installs

The repo must be self-contained after cloning (given only the platform prerequisites: .NET runtime, Node.js, SQL Server). All other tools must be declared inside the repo:

- **.NET tools** → `api/.config/dotnet-tools.json` (restored via `dotnet tool restore`)
- **Node tools** → `devDependencies` in `app/package.json` (available after `npm install`)
- **Infra tools** → declared in the relevant project config

Never work around a missing tool with a global install or bare `npx` — add it to the appropriate manifest instead.

## Code Quality

- No magic strings/numbers — use constants/enums
- Prefer explicit over implicit
- Single responsibility per class/component

## Simplicity First

- Minimum code that solves the problem — nothing speculative
- No abstractions for single-use code; no "flexibility" or configurability that wasn't requested
- No error handling for impossible scenarios
- If it could be half the size, rewrite it — would a senior engineer call this overcomplicated?

## Surgical Changes

- Touch only what the task requires — don't "improve" adjacent code, comments, or formatting
- Don't refactor what isn't broken; match existing style even if you'd do it differently
- Remove only the orphans your own change created — never delete pre-existing dead code, mention it instead
