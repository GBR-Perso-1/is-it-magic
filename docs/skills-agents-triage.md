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
| project-locator | GENERIC **(done)** | Ported 2026-06-04: workspace-walk repointed to the `_workspace-discovery` contract (MARKER=`.git`) — fixes the flat-layout hard-error; scoring kept, examples neutralised; result block `Scope:` → `Parent:`. |
| plugin-architect | GENERIC | About authoring this plugin; explicitly bans stack references |
| plugin-reviewer | GENERIC | Validates plugin conventions only |
| scanner-secrets | GENERIC | Multi-stack pattern lib + `STACK_HINT` param (borderline: leaks `appsettings`/`Controllers`) |
| scanner-injection | GENERIC | C#/Python/Node/Vue patterns as equals (borderline: `Controllers/`, `*DbContext*`) |
| scanner-exposure | GENERIC | Vite/webpack/.NET as equals (borderline: hardcodes `Program.cs`, `vite.config`) |
| azure-investigator | STACK-LEAKED | Hardcodes `az` CLI, App Service, Key Vault, Entra — see Cluster 3 |
| scanner-devbox | STACK-LEAKED → **GENERIC (done)** | Ported 2026-06-04. Same multi-cloud verdict as the other scanners (Azure patterns are coverage, not a lock; AWS/Terraform/generic too). Generalised the `*-credentials-*.ps1` heuristic → any `credential`/`secret`-named script/config file. Different family from the 3 repo scanners (CSV schema, Variant B) — NOT a `_scanner-base` consumer. |
| architect | WHOLESALE | `api/src/Domain`, `Application/Features`, MediatR, EF, Pinia through every phase — see Cluster 1 |
| developer | WHOLESALE | `dotnet ef migrations`, NSwag regen, `npm run type-check`, `ApiClient.ts` — see Cluster 1 |
| test-writer | WHOLESALE | xUnit/FluentAssertions/Moq/MediatR fixtures + Vitest/Pinia — see Cluster 1 |
| reviewer-quality | WHOLESALE | `dotnet format`, `npm --prefix app`, `terraform fmt` — see Cluster 1 |
| reviewer-design | WHOLESALE | MediatR-thin-API, Pinia rules, one-resource-per-TF-module — see Cluster 1 |
| reviewer-perf | WHOLESALE | EF Core `AsNoTracking`/`Include`, MediatR, Vue watchers — see Cluster 1 |

## Skills (17 — `project-init` already deleted)

| Skill | Bucket | Strongest evidence |
|---|---|---|
| devbox-init | GENERIC **(done)** | Ported near-verbatim 2026-06-04. Syncs `rules/` to `~/.claude/` + enables favoured-language LSPs. No deps, no leaks; LSP keys (csharp/typescript/pyright) kept as personal favoured-language config. |
| project-decide | GENERIC | Conversation-only decision layer; nothing hardcoded |
| session-to-skill | GENERIC | Authoring skills; placeholderises project specifics |
| plugin-implement | GENERIC | Authoring plugin artefacts; reads contexts dynamically |
| plugin-commit | GENERIC | Versioning the plugin repo itself |
| project-investigate | STACK-LEAKED | Azure/Entra/MSAL as first-class detection signals (borderline: GENERIC) — see Cluster 3 |
| project-requirements | STACK-LEAKED | Quick-scan hardcodes `*.sln`/`Program.cs`; Delivery table prescribes `api/app/infra` — see Cluster 2 |
| project-implement | STACK-LEAKED | Phase 4 greps `EntityFrameworkCore`/vue; Phase 2 `dotnet test`/`npm test` — see Clusters 1 & 2 |
| project-sync | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: description "`<Scope>.Applications/`" → "sibling projects under the same parent"; Vue/Perso examples neutralised; `_ux-rules` ref + locator `Scope:`→`Parent:` refs fixed. Dep `project-locator` ported alongside. |
| repo-commit | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: `api/app/infra` enum → generic path scope; hardcoded `dotnet`/`npm` test commands → toolchain detection (.sln/.csproj, package.json+lockfile, pyproject/pytest); shared-doc refs fixed. Ported deps `_context-resolution.md` + `_contexts-schema.md` (examples neutralised). |
| repo-git-trigger-workflow | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-03: shortname map → substring-match on discovered workflows; plan/apply gate generalised by keyword; example names neutralised; `_ux-rules` ref + command name fixed. |
| repo-git-env | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: kept whole in base; init source 1 (workflow scan) is the generic backbone; source 2 generalised to "per-env config-file dir" with `.github/appsettings-value/appsettings.json` as a built-in *default*; source 3 path → any `**/*.tf`; Azure/.NET example values neutralised; `_ux-rules` block added. |
| az-query | STACK-LEAKED | Azure substrate OK, but Rise examples (justifi, estateops) + reads `infra-naming.md` — see Cluster 3 |
| devbox-scan-secrets | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: description "Azure configs" → "cloud credentials"; Phase 0 made cross-platform (Windows `USERPROFILE`/`APPDATA` **or** Unix `HOME`/`$XDG_CONFIG_HOME`, matching `devbox-init`). `.azure`/`.aws`/`.ssh` are multi-cloud, kept. Deps `_ux-rules`, `_secret-redaction`, `scanner-devbox` all live. |
| devbox-set-context | STACK-LEAKED → **GENERIC (done)** | De-leaked 2026-06-04: example identifiers neutralised (`Rise-4`/`gbrourhant@rise.fo`/`github-rise`/`rise-env`/`*.Applications` → placeholders, matching `_contexts-schema`); `/platform:contexts` command refs → `/devbox-set-context`. Kept separate from `devbox-init`. Deps `_ux-rules` + `_contexts-schema` live. |
| project-session | WHOLESALE | Full .NET/Quasar/Terraform/Azure dossier; only meaningful on the Rise stack |
| ~~repo-security-scan~~ | ~~WHOLESALE~~ → **GENERIC** | **Re-classified 2026-06-03.** Purpose is generic (orchestrates 3 generic scanner agents); only the description wording + `Rise-4` org-lock were Rise-specific. De-Rised and moved to base; org allowlist (if wanted) can be layered by the rise plugin. |
| repo-ef-sql | WHOLESALE → **MOVED to rise** | Pressure-tested 2026-06-04: genuinely wholesale (no generic core — "generate migration SQL" is not a uniform op across ORMs). Moved verbatim to `rise-dev-plugin/skills/repo-ef-sql/`. Does NOT live in base. First artefact to leave the base. |

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
  - `project-locator` (Phase 1) — **DONE 2026-06-04**: repointed to the contract (MARKER `.git`); flat-layout
    hard-error fixed; result block `Scope:` → `Parent:`.
  - `project-sync` — **DONE 2026-06-04**: description + examples de-leaked; relies on `project-locator` for
    discovery (no longer assumes `*.Applications`).
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
- 2026-06-04 — `repo-ef-sql` **moved out of base** to `rise-dev-plugin/skills/repo-ef-sql/` (verbatim —
  EF/clean-arch layout is correct for Rise repos). First wholesale mover. **Establishes `rise-dev-plugin`
  as the destination for .NET-stack content** (was an open question) — relevant to where the
  `_api-archi-extended.md` holding files and `project-session`'s .NET dossier eventually land.
- 2026-06-04 — `repo-commit` de-leaked into base (STACK-LEAKED → GENERIC): `api/app/infra` enum → generic
  path scope; hardcoded `dotnet`/`npm` test commands → **toolchain detection** (manifest/lockfile-based);
  shared-doc refs fixed to `${CLAUDE_PLUGIN_ROOT}`. Ported its closure: shared `_context-resolution.md`
  (one `rise-qa` example neutralised) and `_contexts-schema.md` (all real identifiers → placeholders).
  Cluster 2: the toolchain-detection logic is inline; flag a shared `_toolchain-detection` contract if
  `project-implement`/`project-requirements` end up needing the same (rule-of-three not yet met).
- 2026-06-04 — `devbox-init` ported into base near-verbatim (GENERIC). No deps, no leaks. Self-references to
  `is-it-magic` are correct (it's the plugin's own init skill); favoured-language LSP keys kept. Decision:
  `devbox-init` and `devbox-set-context` kept **separate** (distinct responsibilities + opposite interaction
  models — autonomous vs interactive CRUD); the `devbox-*` prefix already groups them.
- 2026-06-04 — `devbox-set-context` de-leaked into base (STACK-LEAKED → GENERIC): example identifiers
  neutralised to match `_contexts-schema` (`Rise-4`/`gbrourhant@rise.fo`/`github-rise`/`rise-env`/
  `*.Applications` paths → placeholders); `/platform:contexts` command references fixed to
  `/devbox-set-context`. Deps `_ux-rules` + `_contexts-schema` already live — no dangling refs.
- 2026-06-04 — `devbox-scan-secrets` de-leaked into base (GENERIC) + its `scanner-devbox` dependency ported.
  Description neutralised ("Azure configs" → "cloud credentials"); Phase 0 made cross-platform (Windows
  `USERPROFILE`/`APPDATA` or Unix `HOME`/`$XDG_CONFIG_HOME`). `scanner-devbox` is multi-cloud (Azure patterns
  are coverage, not a lock); `*-credentials-*.ps1` heuristic generalised to any credential/secret-named
  script/config file. **Correction**: `scanner-devbox` is a *different family* from the 3 repo scanners
  (CSV schema, Variant B) — NOT a `_scanner-base` consumer, so that extraction only ever needed the 3 repo
  scanners (all live) and is unblocked now.
- 2026-06-04 — `project-sync` de-leaked into base (STACK-LEAKED → GENERIC) + its `project-locator` dependency
  ported. `project-sync`: description "`<Scope>.Applications/`" → "sibling projects under the same parent";
  Vue/Perso examples neutralised; `_ux-rules` ref fixed; locator `Scope:`→`Parent:` references updated.
  `project-locator`: **closes the marker-walk backlog item** — Phase 1–2 (`*.Applications` Python walk)
  replaced with the `_workspace-discovery` contract (MARKER=`.git`), fixing the flat-layout hard-error;
  scoring kept, `fi--justi-fi` examples neutralised, result block `Scope:` → `Parent:`. The
  `_workspace-discovery` contract now has its second live consumer (rule-of-three confirmed sound).
