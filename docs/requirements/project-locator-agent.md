# Dev Workflow Plugin — Project Locator Agent Requirements

## Vision

Add a **project locator agent** to the plugin — a reusable component that resolves a natural-language project name (e.g. "Justifi", "Kyriba BI", "estate hub") to a verified local path and git metadata. Any skill in the plugin can spawn this agent to gain cross-project awareness without re-implementing path discovery logic.

---

## Epics

### Epic 1: Project Locator Agent

**Goal**: Enable any skill to resolve a project by name to its local path and git identity, regardless of where Claude is currently running.

#### Requirements

- **REQ-1.1**: The agent accepts a natural-language project name as its input (e.g. "Justifi", "the wealth pilot project", "justifi").
- **REQ-1.2**: The agent discovers the workspace root dynamically by walking up from the current working directory until it finds a parent that contains one or more `*.Applications` subdirectories.
- **REQ-1.3**: The agent scans every `*.Applications` folder found under the discovered workspace root.
- **REQ-1.4**: Within each scope folder, the agent considers only subdirectories that contain a `.git` folder as valid project candidates (ignoring non-repo folders such as `.sql-utilities`, `.archive`, `.sandbox`).
- **REQ-1.5**: The agent matches the input against two signals per candidate: (a) the folder name with any prefix stripped (e.g. `fi--justi-fi` → `justi-fi`, `justifi`), and (b) the remote repo name extracted from `.git/config` (the `url =` line under `[remote "origin"]`).
- **REQ-1.6**: Matching is fuzzy and case-insensitive — partial matches and common abbreviations are accepted.
- **REQ-1.7**: When a single best match is found, the agent returns it with a confidence level (High / Medium / Low) and a one-line rationale (e.g. "Matched `fi--justi-fi` via folder name similarity").
- **REQ-1.8**: When multiple candidates score similarly, the agent returns all of them ranked by confidence, and the calling skill or user selects the intended one.
- **REQ-1.9**: The agent returns the following payload to the calling skill:
  - Absolute local path
  - Scope name (e.g. `Rise.Applications`)
  - Remote origin URL
  - Current branch name
  - Confidence level
- **REQ-1.10**: When the workspace root cannot be determined (cwd is entirely outside a `*.Applications` structure), the agent stops with a clear error message indicating the working directory and what it expected to find.
- **REQ-1.11**: When no candidates match the input at any confidence level, the agent stops with a clear error listing the scopes and candidate count it searched.

#### Decisions & Assumptions

- Workspace root is `C:\Workspace\Dev\` in practice, but the agent derives it dynamically — no hard-coded paths.
- Drive letter is not assumed; the walk-up strategy handles any drive.
- Prefix stripping (e.g. `fi--`, `it--`, `h4--`, `eapa--`) is heuristic — any segment before `--` is treated as a prefix and stripped for matching purposes.
- "Confidence" is not precisely defined yet — rough target: High = unambiguous name match, Medium = partial/fuzzy, Low = only remote URL matched.

---

### Epic 2: Skill Integration Contract

**Goal**: Define how existing and future skills consume the locator agent, so the calling convention is consistent.

#### Requirements

- **REQ-2.1**: Any skill that needs to operate on a project *not* the current working directory must delegate path resolution to the project locator agent rather than implementing its own discovery logic.
- **REQ-2.2**: The locator agent is a plugin agent (`agents/project-locator.md`) — skills reference it via `${CLAUDE_PLUGIN_ROOT}/agents/project-locator.md`, consistent with the existing agent convention.
- **REQ-2.3**: Skills that call the locator must pass the resolved absolute path as the working context for any subsequent file operations or sub-agent spawns.
- **REQ-2.4**: If the locator returns a Medium or Low confidence result, the calling skill must surface the match to the user for confirmation before proceeding (e.g. "Located `fi--justi-fi` in `Rise.Applications` — is this the right project?").

#### Decisions & Assumptions

- No changes to existing skills are required in this epic — this is a forward contract for new skills and opt-in adoption by existing ones.
- `project-sync` already has partial discovery logic; it may eventually delegate to the locator, but that migration is out of scope here.

---

### Epic 3: User-Facing Locate Skill (Optional)

**Goal**: Expose the locator directly as a slash command for exploratory use and debugging.

#### Requirements

- **REQ-3.1**: A `/locate-project <name>` skill allows the user to resolve a project name interactively and see the full locator output (path, scope, remote, branch, confidence).
- **REQ-3.2**: The skill is a thin wrapper over the locator agent — no additional logic.

#### Decisions & Assumptions

- This is a "nice to have" — the primary value is in programmatic use by other skills (Epic 2). Deferred if effort is needed elsewhere.

---

## Priorities

| Priority | Epic / Requirement | Rationale |
|----------|--------------------|-----------|
| 1 | Epic 1 — full locator agent | Core capability; everything else depends on it |
| 2 | REQ-2.1, REQ-2.2, REQ-2.3, REQ-2.4 — integration contract | Needed for any skill to actually use the agent |
| 3 | Epic 3 — user-facing skill | Useful but not blocking |

## Out of Scope

- Migrating `project-sync`'s existing SCOPE_ROOT logic to use the locator agent (future opt-in).
- A configured/static workspace root — dynamic discovery covers the need.
- Cross-machine or remote project resolution.
- Projects that don't follow the `*.Applications` folder convention.
