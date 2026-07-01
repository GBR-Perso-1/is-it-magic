---
name: project-safe-npm-upgrade
description: >
  Upgrade a JavaScript/TypeScript project's npm dependencies to their latest
  stable versions with controlled risk — bump safe minor/patch and low-risk
  tooling majors while deliberately excluding breaking majors, verify with the
  project's own gates, then clean up audit vulnerabilities. Never commits.
---

## Important rules

Read and follow all rules in `${CLAUDE_PLUGIN_ROOT}/skills/shared/_ux-rules.md`.

## Context

Use this when a user asks to "upgrade the packages to the latest stable version"
without wanting a risky big-bang migration. It separates cheap, safe updates from
breaking major upgrades, lets the user choose how far to go, proves the result with
the project's existing verification scripts, and then reduces the `npm audit` surface
without pulling in the excluded majors.

## Prerequisites

- A Node/npm project with a `package.json` and a lockfile.
- The project defines verification scripts (some subset of type-check, lint, test, build).
- `npm` available; network access to the registry.

## Placeholders

Before running this skill, substitute all `{{PLACEHOLDER}}` tokens:

| Placeholder | Description |
|---|---|
| {{APP_DIR}} | Directory holding the target `package.json` (e.g. the repo root, or a `app/` / `frontend/` subfolder in a monorepo). |
| {{VERIFY_COMMANDS}} | The project's own verification scripts to run after upgrading, in order — e.g. `npm run type-check`, `npm run lint`, `npm run test`, `npm run build`. Discover them from the `scripts` block; run whichever exist. |

## Steps

1. **Survey.** From `{{APP_DIR}}`, run `npm outdated`. Read `package.json` to see the declared ranges and the `engines`/Node constraint. Note the installed Node version (`node --version`) — some majors raise the minimum.

2. **Classify every outdated package into three buckets:**
   - **Safe** — new version is within the current major (minor/patch). Low risk.
   - **Low-risk major** — tooling that upgrades cleanly in practice: linters and their plugins, formatters, DOM test environments, dev CLIs, tsconfig presets.
   - **High-risk major** — the load-bearing toolchain: the build tool (e.g. Vite), the test framework (e.g. Vitest), the state library, the router, the language compiler (TypeScript) and its type-checker, and **anything touching authentication**. These carry migration work.

3. **Confirm scope with the user** via `AskUserQuestion` (single question, recommended option first): safe-only / safe + low-risk majors / everything / everything including auth. Auth-related majors are guardrailed — never include them without explicit opt-in. Let the answer define the target set.

4. **Vet each in-scope major BEFORE editing** — do not trust "latest" blindly:
   - `npm view <pkg>@<targetMajor> peerDependencies engines` for each.
   - **Exclude** any major whose peer requires an *excluded* major (classic trap: a build-tool plugin's new major requires the next build-tool major you chose to skip — keep the plugin on its current major).
   - **Exclude** any major that drags in unwanted peers (e.g. framework-specific peers irrelevant to this project) when the package is low value.
   - Confirm the installed Node satisfies each `engines` field.
   - Check any consuming config file (e.g. the ESLint flat config) for API the new major removes.

5. **Edit `package.json`** — set the in-scope packages to `^<latest-allowed>`; leave every excluded/coupling-locked package pinned at its current major. Keep peer-coupled pairs consistent (e.g. a testing helper pinned to match its host library's major).

6. **Install.** Run `npm install`. If it fails with `ERESOLVE` caused by a stale lockfile/tree, do a **clean reinstall**: delete `node_modules` and the lockfile, then `npm install` again. Missing peer deps are auto-installed by npm; note any deprecation warnings but don't chase transitive ones yet.

7. **Repair breaking config from tooling majors.** When a linter/formatter major tightens a rule's defaults and flags pre-existing code, prefer restoring prior behavior via a rule option over refactoring source — a dependency upgrade should not silently trigger a rename/refactor that ripples into imports or routing. (Example seen: `unicorn/filename-case` gained `checkDirectories: true` by default; set it to `false` to preserve behavior.)

8. **Verify.** Run `{{VERIFY_COMMANDS}}` in order. All must pass. Treat expected `console.error` output from failure-path tests as noise — confirm the suite summary is green, not the absence of red text.

9. **Audit — triage.** Run `npm audit`. Group findings into **chains** by their root vulnerable package. For each chain determine: is the culprit a *direct* dependency, a *transitive* one, and is it actually used (grep the codebase/scripts/config for real references)?

10. **Audit — fix the safe wins:**
    - **Unused direct dependency** in the chain → remove it from `package.json` (verify it's referenced nowhere but its own manifest line first).
    - **Vulnerable transitive dep whose top-level copy is already patched** → add an `overrides` entry scoped to the consuming package, forcing the patched version (use `"<dep>": "$<dep>"` to reuse the root-resolved version).
    - **Chain only fixable by an excluded major** → defer it; record it explicitly with severity and why (e.g. dev-server-only, needs the excluded build-tool major).

11. **Re-audit and re-verify.** Reinstall, run `npm audit`. When npm's human summary severity looks inflated, get ground truth with `npm audit --json` (inspect the actual vulnerable package list) — npm reports the *effective* severity a package participates in, which can overstate counts. Re-run the test suite to confirm any `overrides` didn't break anything.

12. **Report, don't commit.** Present a version table (declared vs installed), the config changes made, and the deferred vulnerabilities with rationale. Leave the working tree uncommitted for the user to review unless they explicitly ask to commit.

## Verification

- `npm outdated` shows only the intentionally-excluded majors remaining (`Current == Wanted` for everything else).
- All `{{VERIFY_COMMANDS}}` pass.
- `npm audit` (cross-checked with `--json`) shows only the deferred chains, each traceable to an excluded major.
