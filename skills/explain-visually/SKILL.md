---
name: explain-visually
description: "First-pass orientation to an application, for a human reader — diagram-led and bounded. Produces four sections in order: data model, users and roles, workflow, and data ownership (what this system is the system of record for, versus what it borrows from elsewhere). Use this when the user wants the broad picture of an app or system rather than a re-explanation of something already said — 'what is this app', 'explain this app to me', 'give me the big picture', 'I'm new to this repo', 'how does this thing work overall', 'draw me the architecture', 'too much detail, just show me the shape'. Explicitly not for internal wiring: no module dependency maps, no import graphs, no per-function decision trees."
---

## Important rules

Read and follow all rules in `${CLAUDE_PLUGIN_ROOT}/skills/shared/_ux-rules.md`.

## Constraints

- **Read-only on source.** The only permitted write is the orientation file in Phase 3, and only after the persistence gate.
- **Altitude cap.** You are NOT mapping the internals — no module dependency maps, no `require`/import graphs, no per-function decision trees, no class diagrams of implementation types. You are answering: what does this system hold, who uses it, how does work flow through it, and what does it own?
- **Length bound.** The whole deliverable's prose should fit in roughly 200-400 words — excluding diagrams and tables.
- **Diagram bound.** At most one diagram per section — including the Workflow section, whose single diagram covers only the headline flows that fit within the cap. Each diagram is at most ~12 nodes. A diagram that needs more nodes is a wiring map and is out of scope — say what was elided in one line instead.
- **Terminal substitute cap.** The Phase 2 ASCII/table substitutes inherit the same ~12-node cap as the diagram they replace. The terminal view is a full representation of this deliverable, not a lesser one — since "Neither" is a valid Phase 3 choice, it may be the only artefact the user ever sees. Where content exceeds the cap, name what was elided in one line, exactly as the diagram bound requires.
- **Render rule.** Mermaid never goes to the terminal. Terminal output uses ASCII flows and tables; mermaid appears only inside a written `.md` file or a rendered Artifact. Printing unrendered mermaid source at the user is a failure, not a fallback.
- **Diagram honesty.** Where a relationship or an owner cannot be determined statically, mark it `Unclear` rather than drawing a plausible edge.

## Input

`$ARGUMENTS` — optional: a path to the app to orient on. Default to the current working directory when empty.

- If the argument is a path that does not resolve, ask once via `AskUserQuestion`: "`<path>` doesn't resolve — what should I orient on?" with options `Use the current working directory` / `Let me give another path`.
- If the target is plainly not an application or codebase (e.g. a single document, a data file, an empty directory), say so in one line and explain what it actually is directly, in prose — do not force the four-section template onto it, and do not route to another skill.

## Phase 1 — Scan (spawn with override)

Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/codebase-explorer.md`, passing:

```
IMPORTANT: you are being used for a diagram-led human orientation, not a business overview.

This countermand replaces — not supplements — your own instructions:
- Ignore your Output Format section entirely; produce only the format below.
- Your Exploration Strategy is replaced in full by the scan order below. Its step 5, external
  clients and integrations, is mandatory, not optional — it is the sole evidence source for
  section 4 (data ownership) and must not be skipped for speed.
- "Use plain business language — avoid technical jargon" does not apply to sections 1 and 4:
  entity names, table names, and external system names are the content there, not jargon to
  translate away.

Altitude cap: you are NOT mapping the internals — no module dependency maps, no `require`/import
graphs, no per-function decision trees, no class diagrams of implementation types. You are
answering: what does this system hold, who uses it, how does work flow through it, and what does
it own?

Bounds: the whole deliverable's prose should fit in roughly 200-400 words, excluding diagrams and
tables. Each section's content must fit within a ~12-node diagram once rendered — if a section has
more, keep the ~12 that matter most and name what was elided in one line. Where a relationship or
an owner cannot be determined statically, mark it `Unclear` rather than drawing a plausible edge.

Target: <resolved path from Input>

Scan order (replaces your own Exploration Strategy):
1. Metadata — README, CLAUDE.md, project-context.md, package.json / .csproj / solution files.
2. Data model — entity/model definitions, migrations, schema files.
3. Entry points / API surface — controllers, routes, API client definitions.
4. UI / roles — pages, navigation, router definitions, auth/role guards.
5. External clients and integrations — outbound API clients, sync jobs, webhooks, third-party
   SDKs. Mandatory: this is the only evidence for section 4 below.

Return content only — no mermaid, no ASCII diagrams. Structured content for each of these four
sections, in order:

---

### 1. Data model
The domain nouns and their relationships — first, because it is the most reliable statement of
what the business cares about. For each entity: name, key fields, what it relates to, and the
cardinality of that relationship, stated exactly where the schema declares it, else `Unclear`.

### 2. Users / roles
Who uses it, in what role, internal vs external. For each role: name, internal/external, the
capability cluster (what they do).

### 3. Workflow
The main end-to-end processes — up to 3-5 headline flows, as the ~12-node cap allows, each as an
ordered step chain (A -> B -> C). Keep the total steps across all flows within the ~12-node cap;
if more flows exist than fit, name the elided ones in one line rather than listing every step of
every flow.

### 4. Data ownership
What this system is the system of record for, versus what it reads or borrows. For each piece of
data: the data itself, the system of record, and this system's role.

Inference rubric:
- Local schema / migrations / entity definitions ⇒ **owned**.
- An external API client or DTO with no local persistence ⇒ **borrowed (read)**.
- A sync job, mirror table, or cache of remote data ⇒ **copy, not owner**.
- A client that POSTs/PUTs to another system ⇒ **writes back, not owner**.
- Anything not decidable from these ⇒ `Unclear`.
- If nothing external is found, state "self-contained — system of record for everything it holds" rather than omitting the section.
```

Wait for the agent to return the four sections' content before proceeding to Phase 2. This content is the single payload both later phases render from — Phase 2 and Phase 3 are pure renderers, never a second scan.

## Phase 2 — Terminal rendering

Render the Phase 1 content as its terminal substitute — ASCII and tables only, no mermaid:

| # | Section | Terminal substitute |
|---|---------|---------------------|
| 1 | Data model | table: entity \| key fields \| relates to |
| 2 | Users / roles | table: role \| internal/external \| what they do |
| 3 | Workflow | numbered ASCII arrow chains (`A → B → C`) |
| 4 | Data ownership | table: data \| system of record \| this system's role |

Each substitute inherits the ~12-node cap stated in Constraints; elisions are named exactly as
Phase 1 named them. This is the same content rendered a second way, not a second deliverable — the
200-400 word prose bound in Constraints applies once, to the underlying content, and is not doubled
by rendering it again here.

## Phase 3 — Persistence gate

Diagram type per section, used when rendering to mermaid below:

| # | Section | Diagram type |
|---|---------|---------------|
| 1 | Data model | `erDiagram` — render the stated cardinality on each relation; where none was stated, use an unlabelled relation or `Unclear`, never invent one |
| 2 | Users / roles | `flowchart LR` — actor → capability cluster |
| 3 | Workflow | `flowchart` — one diagram covering the headline flows kept within the ~12-node cap; `sequenceDiagram` only when exactly one headline flow was kept |
| 4 | Data ownership | `flowchart LR` — this-system boundary vs external systems, edges labelled with the rubric's own values: `owned` / `borrowed (read)` / `copy, not owner` / `writes back, not owner` / `Unclear` |

Ask via `AskUserQuestion`:

- Question: "How would you like to keep this orientation? (Diagrams only render in a file or an Artifact — the terminal view above used ASCII substitutes.)"
- Options:
  1. `Markdown file in .claude/reports/ (Recommended)`
  2. `Rendered Artifact`
  3. `Both`
  4. `Neither — the terminal version is enough`

Handle the answer:

- **Markdown file** → render the Phase 1 content as mermaid (per the table above) and write `.claude/reports/orientation-<YYYY-MM-DD>.md`, mirroring the write pattern in `agents/repo-archaeologist.md`. Title `# <App> — Orientation`, followed by the four sections with their mermaid blocks fenced.
- **Rendered Artifact** → render the same content as mermaid into an Artifact where the surface supports it. Where the surface has no Artifact capability, say so in one line and fall back to the Markdown file — never to printing mermaid.
- **Both** → write the file first, then render the Artifact from it.
- **Neither** → end here; the terminal rendering from Phase 2 stands.

## Conversation Style

- British English throughout.
- State findings as facts grounded in file locations — never speculate.
- Close with a one-line forward pointer (`/project-investigate` or `/project-requirements`) — no gate.
