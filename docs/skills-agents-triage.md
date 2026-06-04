# Skills & Agents Triage — Base vs Specialized

> Reference map produced 2026-06-03 (read-only triage). Classifies all base-plugin agents and
> skills for the `is-it-magic` (base) → specialized-plugin split. Companion to
> [`plugin-model.md`](./plugin-model.md) (the litmus) and [`SESSION-FRAMING.md`](./SESSION-FRAMING.md).
> This is a planning artefact — no code was changed to produce it.

## Litmus used

`is-it-magic` is the BASE plugin — stack-agnostic, "how I work on any project", user-level.
Specialized plugins (a company "rise" plugin, or a ".NET clean-architecture stack" plugin) layer on
top and own stack/company specifics. Each file is placed in exactly one bucket:

- **GENERIC** — purpose AND content stack-agnostic; works on any project. Naming a common tool is
  fine if it carries no ecosystem specifics. Plugin-authoring artefacts count as GENERIC. A cloud
  provider used as a **universal substrate** (Azure) may stay GENERIC if parameterised.
- **STACK-LEAKED** — generic *purpose*, but content hardcodes stack/company specifics that should be
  extracted (repo layout `api/app/infra`, `dotnet`/`npm`/`terraform`, EF/MediatR/Vue/Quasar/Pinia,
  company names, MSAL/Entra).
- **WHOLESALE-SPECIALIZED** — only meaningful for a specific stack/company; should leave the base.

## Agents (16)

| Agent | Bucket | Strongest evidence |
|---|---|---|
| codebase-explorer | GENERIC | Stack-agnostic; names README/package.json/.csproj only as examples |
| repo-archaeologist | GENERIC | Multi-stack by design (`.cs`, Python, EF/Prisma/SQLAlchemy as equals) |
| project-locator | GENERIC | Pure cwd-walk; forbids hardcoded paths |
| plugin-architect | GENERIC | About authoring this plugin; explicitly bans stack references |
| plugin-reviewer | GENERIC | Validates plugin conventions only |
| scanner-secrets | GENERIC | Multi-stack pattern lib + `STACK_HINT` param (borderline: leaks `appsettings`/`Controllers`) |
| scanner-injection | GENERIC | C#/Python/Node/Vue patterns as equals (borderline: `Controllers/`, `*DbContext*`) |
| scanner-exposure | GENERIC | Vite/webpack/.NET as equals (borderline: hardcodes `Program.cs`, `vite.config`) |
| azure-investigator | STACK-LEAKED | Hardcodes `az` CLI, App Service, Key Vault, Entra — see Cluster 3 |
| scanner-devbox | STACK-LEAKED | Azure category baked in (`ARM_CLIENT_SECRET`, `.tfstate`) — see Cluster 3 |
| architect | WHOLESALE | `api/src/Domain`, `Application/Features`, MediatR, EF, Pinia through every phase — see Cluster 1 |
| developer | WHOLESALE | `dotnet ef migrations`, NSwag regen, `npm run type-check`, `ApiClient.ts` — see Cluster 1 |
| test-writer | WHOLESALE | xUnit/FluentAssertions/Moq/MediatR fixtures + Vitest/Pinia — see Cluster 1 |
| reviewer-quality | WHOLESALE | `dotnet format`, `npm --prefix app`, `terraform fmt` — see Cluster 1 |
| reviewer-design | WHOLESALE | MediatR-thin-API, Pinia rules, one-resource-per-TF-module — see Cluster 1 |
| reviewer-perf | WHOLESALE | EF Core `AsNoTracking`/`Include`, MediatR, Vue watchers — see Cluster 1 |

## Skills (17 — `project-init` already deleted)

| Skill | Bucket | Strongest evidence |
|---|---|---|
| devbox-init | GENERIC | Syncs `rules/` to `~/.claude/`; LSP keys are favoured-language config |
| project-decide | GENERIC | Conversation-only decision layer; nothing hardcoded |
| session-to-skill | GENERIC | Authoring skills; placeholderises project specifics |
| plugin-implement | GENERIC | Authoring plugin artefacts; reads contexts dynamically |
| plugin-commit | GENERIC | Versioning the plugin repo itself |
| project-investigate | STACK-LEAKED | Azure/Entra/MSAL as first-class detection signals (borderline: GENERIC) — see Cluster 3 |
| project-requirements | STACK-LEAKED | Quick-scan hardcodes `*.sln`/`Program.cs`; Delivery table prescribes `api/app/infra` — see Cluster 2 |
| project-implement | STACK-LEAKED | Phase 4 greps `EntityFrameworkCore`/vue; Phase 2 `dotnet test`/`npm test` — see Clusters 1 & 2 |
| project-sync | STACK-LEAKED | Assumes `.vue` + `<Scope>.Applications/` layout (borderline: GENERIC) |
| repo-commit | STACK-LEAKED | `dotnet test api/{sln}`, `npm run --prefix app test` — see Cluster 2 |
| repo-git-trigger-workflow | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-03: shortname map → substring-match on discovered workflows; plan/apply gate generalised by keyword; example names neutralised; `_ux-rules` ref + command name fixed. |
| repo-git-env | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: kept whole in base; init source 1 (workflow scan) is the generic backbone; source 2 generalised to "per-env config-file dir" with `.github/appsettings-value/appsettings.json` as a built-in *default*; source 3 path → any `**/*.tf`; Azure/.NET example values neutralised; `_ux-rules` block added. |
| az-query | STACK-LEAKED | Azure substrate OK, but Rise examples (justifi, estateops) + reads `infra-naming.md` — see Cluster 3 |
| devbox-scan-secrets | STACK-LEAKED | Fixed list `.azure/`/`.aws/`/`.ssh/` (borderline: GENERIC) — see Cluster 3 |
| devbox-set-context | STACK-LEAKED | Schema is GitHub+Entra+ADO; examples `Rise-4`, `gbrourhant@rise.fo` — see Cluster 3 |
| project-session | WHOLESALE | Full .NET/Quasar/Terraform/Azure dossier; only meaningful on the Rise stack |
| ~~repo-security-scan~~ | ~~WHOLESALE~~ → **GENERIC** | **Re-classified 2026-06-03.** Purpose is generic (orchestrates 3 generic scanner agents); only the description wording + `Rise-4` org-lock were Rise-specific. De-Rised and moved to base; org allowlist (if wanted) can be layered by the rise plugin. |
| repo-ef-sql | WHOLESALE | `dotnet ef migrations script` generator — canonical wholesale case |

**Counts:** Agents — 8 GENERIC, 2 STACK-LEAKED, 6 WHOLESALE. Skills — 5 GENERIC, 10 STACK-LEAKED, 3 WHOLESALE.
*(Revised in progress: `repo-security-scan` moved WHOLESALE → GENERIC on 2026-06-03 — now 6 GENERIC / 10 STACK-LEAKED / 2 WHOLESALE.)*

## The 3 decision clusters

The 33 files reduce to three decisions plus a scrub.

### Cluster 1 — The implementation pipeline (6 agents + `project-implement`)
`architect`, `developer`, `test-writer`, `reviewer-quality`, `reviewer-design`, `reviewer-perf` are
*generic in concept, wholesale-coupled in implementation*. Their fate is the **rewire already
scoped**: load `_api-archi.md` + `_api-archi-extended.md` / `_app-archi-extended.md` instead of
hardcoding layout and commands. De-leak them → a generic shell stays in base, the stack saturation
moves to the specialized archi docs. **One decision governs all seven.** Unblocks the deferred merge
of the `*-archi-extended` holding files.

### Cluster 2 — The `api/app/infra` + `dotnet/npm/terraform` leak (5 skills)
`repo-commit`, `repo-git-trigger-workflow`, `repo-git-env`, `project-implement`,
`project-requirements` all leak the *same* repo-layout + command-triad. Extract it **once** into a
parameterised stack-config read at runtime (the `contexts.json` pattern already exists here) and all
five de-leak in a single move. **One decision, not five.**

### Cluster 3 — The Azure question (consistency flag)
`azure-investigator`, `az-query`, `scanner-devbox`, `devbox-scan-secrets`, `devbox-set-context`,
`project-investigate`'s Azure branch, and `repo-git-env`'s Azure secrets are "specialized" **only if
Azure is treated as non-base**. We already ruled the opposite — **Azure is the universal substrate**
(why `infra-naming.md` stayed in base). Applied consistently, these **stay in base**; the only work
is scrubbing company-name leaks (`Rise-4`, `estateops`, `gbrourhant@rise.fo`). Mostly "scrub
examples", not "move out". **Confirm the Azure stance once, then it frames the whole cluster.**

### Genuinely wholesale — no ambiguity
`repo-ef-sql`, `repo-security-scan` (Rise-locked to `Rise-4`), `project-session` (Rise dossier).
These clearly leave the base. Clean wins, no judgment calls.

## Recommended sequence (agents-first)
1. **Cluster 1** — pipeline rewire (open thread; highest value; unblocks the archi-extended merge).
2. **Cluster 3** — confirm Azure-substrate stance, then scrub company names.
3. **Cluster 2** — extract the layout/command convention into parameterised stack-config.
4. **Wholesale movers** — relocate `repo-ef-sql`, `repo-security-scan`, `project-session` to the specialized plugin.

## Consolidation backlog (cross-artefact, revisit later)
- **Layout-agnostic marker-walk** — discovery must NOT key on the `*.Applications` folder name: that
  holds on the work machine but breaks on the flat personal layout (`<drive>:\workspaces\dev\<projects>`).
  The robust pattern is "walk up from cwd (bounded levels) + scan child/grandchild dirs for a **marker
  file**", parameterised by marker: `.claude-plugin/plugin.json` for plugin repos, `.git` for projects.
  Shared kernel extracted to **`skills/shared/_workspace-discovery.md`** (the "Workspace Discovery
  Contract", parameterised by MARKER) — 2026-06-03.
  - `session-to-skill` (Step 3.3) — **DONE 2026-06-03**: references the contract (MARKER `.claude-plugin/plugin.json`).
  - `project-locator` (Phase 1) — **TODO**: currently hard-errors "Workspace root not found" on the flat
    layout; repoint to the contract (MARKER `.git`) when reached in the agents phase.
  - `project-sync` — **TODO**: whole concept is "siblings in a `*.Applications` folder"; repoint to the
    contract then filter to siblings under the same parent when rewritten.
- **`_scanner-base.md` — hoist triplicated scanner boilerplate** — `scanner-secrets`/`injection`/`exposure`
  repeat ~25 near-identical lines (Guardrails, Inputs, Finding schema, Phase 1 scope-resolution intro,
  findings/pattern/grep caps). Extract to `skills/shared/_scanner-base.md` (mirroring `_secret-redaction.md`).
  **Defer to the scanner-agent review** so the 4th consumer (`scanner-devbox`, still in backup) is in hand
  before settling the shape once. (Flagged by external review 2026-06-04.)

## Progress log
- 2026-06-03 — `session-to-skill` rewritten into base (GENERIC, surgical leak-scrub): fixed `_ux-rules.md`
  reference to `${CLAUDE_PLUGIN_ROOT}/...`; removed dead machine-specific path check in Phase 5; then
  repointed discovery to the new `_workspace-discovery.md` contract.
- 2026-06-03 — `repo-security-scan` rewritten into base (re-classified GENERIC): dropped the `Rise-4`
  org-lock for a confirm-before-clone gate; de-Rised description; fixed `/tmp` → OS-aware temp dir;
  fixed command name to `/repo-security-scan`. Org allowlist left for the rise plugin to layer if wanted.
- 2026-06-03 — **dependency closure** of `repo-security-scan` ported into base (was missed initially —
  the skill referenced agents not yet live): `scanner-secrets`, `scanner-injection`, `scanner-exposure`
  (all GENERIC), plus shared `_secret-redaction.md`. The three scanners' surface file-targets were
  **parameterised by `STACK_HINT`** (generic baseline always + per-stack globs; empty hint → all sets),
  closing the "STACK_HINT declared but unused" smell. `repo-security-scan` closure now complete.
- 2026-06-03 — `repo-git-trigger-workflow` de-leaked into base (STACK-LEAKED → GENERIC): hardcoded
  shortname→filename map replaced with substring-match against discovered workflows; `infra` plan→apply
  auto-sequence generalised to keyword-based plan/apply pairing; company example names neutralised;
  `_ux-rules` reference + command-name mismatch fixed. No dangling deps (only `_ux-rules`, already live).
- 2026-06-04 — acted on external review of the security-scan slice: fixed `repo-security-scan` agent-spawn
  paths to the mandated `${CLAUDE_PLUGIN_ROOT}/agents/<name>.md` form (#2, convention/portability bug) and
  bound `SCAN_DEPTH`/`SCAN_ROOT` explicitly (#3, clarity). `_scanner-base.md` extraction (#1) deferred to the
  scanner-agent review; Variant-B forward-refs (#4) and `session-to-skill` verbosity (#5) intentionally left.
- 2026-06-04 — `repo-git-env` de-leaked into base (STACK-LEAKED → GENERIC), kept whole (no split — a
  specialized plugin cannot inject steps into a base skill, so splitting = duplication). Init source 2
  generalised from hardcoded `appsettings.json` to a "per-env config-file directory" pattern with the
  `.github/appsettings-value/<env>/appsettings.json` layout as a built-in default (still auto-matches Rise);
  source 3 path generalised to any `**/*.tf`; config-format + apply examples neutralised (dropped
  `AZURE_*`/`APPSETTINGS_JSON`); added the `_ux-rules` Important-rules block. Dep: `_ux-rules` (already live).
