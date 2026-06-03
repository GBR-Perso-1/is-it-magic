# General Engineering Standards

- Windows environment — use PowerShell for scripts
- British English in all comments and documentation

## Git

- Prefer `/repo-commit` for commits — it runs tests, applies the conventional format, and gates the push
- Conventional commits: `type(scope): description` (feat / fix / chore / refactor) — applies to direct commits too
- Commit directly on `main` — commits may span multiple concerns — **unless a project rule requires otherwise, in which case the project rule takes precedence**
- Never push to remote without user confirmation

## Dependencies — No Global Installs

The repo must be self-contained after cloning, given only the platform prerequisites (language runtimes and any required services). All other tools must be declared inside the repo, in the appropriate per-language or per-tool manifest, so they are restored as part of normal setup.

Never work around a missing tool with a global install or an ad-hoc fetch — add it to the appropriate manifest instead.

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
