# Rise way of working vs how Anthropic builds software — open items

> **Purpose**: the remaining open backlog from confronting the full Rise/is-it-magic operating model —
> the tooling, the doctrine, *and* the actual practice — against *"How building software is changing at
> Anthropic"* (The Pragmatic Engineer, Gergely Orosz, 28 Jul 2026; interviews with Katelyn Lesse,
> Jarred Sumner, Thariq Shihipar).
> **Analysis captured**: 2026-08-04. **Last revised**: 2026-08-07.
>
> **Decisions taken from this review now live as ADRs** in [`adr/`](adr/README.md). This document keeps
> only the analysis and the items on which nothing has been decided. When an item here is decided, it
> moves out to an ADR and leaves a pointer behind.
>
> **Baseline**: `is-it-magic` v6.1.7 (19 skills, 14 agents, 6 rules) + `it--claude-rise-plugin`
> (8 skills, engineering handbook ×2 variants, project-coach, Rise conventions). Operator context:
> one lead engineer using the `investigate → decide → requirements → implement → commit → deploy`
> suite; juniors distil the lead's way of working through the handbook + `/project-coach`.

---

## The operating model (as compiled from every skill and md file)

Five codified layers with one doctrine running through them — plus a sixth layer that is real but
**uncodified**:

1. **Machine** — `devbox-init`, `devbox-set-context`, `devbox-scan-secrets`: reproducible workstation,
   accounts as data.
2. **Ambient discipline** — 6 auto-loaded rules; `rules/general.md` "Reason Before You Act" is the same
   failure-mode doctrine as the handbook's "catch yourself" list. The discipline is encoded **three
   times**: rules (every AI session), handbook (juniors + AI in Rise projects), constraint blocks
   (every pipeline agent). → [ADR-0005](adr/0005-inject-an-explicit-failure-modes-list.md)
3. **Project bootstrap** — `project-init`, `repo-scaffold`, conventions as layered data
   (`apply-conventions` base + Rise overlays) consumed by deliberately stack-agnostic agents.
4. **The lead's lifecycle** — investigate → decide → requirements → implement (4 rigour modes,
   RED→GREEN where governed) → commit → deploy. Read-only phases strictly separated from mutating ones.
   → [ADR-0004](adr/0004-scale-planning-rigour-to-complexity.md),
   [ADR-0008](adr/0008-gate-every-mutating-phase-on-a-human.md)
5. **People + compounding** — handbook + coach to *manufacture* judgment in juniors; `session-to-skill`
   to turn solved problems into skills (the Rise plugin's `fix-openapi-enum-schema` and
   `migrate-navigation-to-static` are its visible outputs — the loop runs).
   → [ADR-0001](adr/0001-manufacture-judgment-through-codified-doctrine.md),
   [ADR-0006](adr/0006-compound-solved-problems-into-skills.md)
6. **Uncodified: session-level fan-out.** The lead runs **5–10 parallel Claude Code sessions** across
   different repos — or the same repo — so multiple `/project-implement` runs execute simultaneously.
   This layer exists only in practice: no skill, rule, or handbook line knows about it.

**Structural fact**: the junior's doctrine and the lead's automation are the same shape — handbook
lifecycle steps 1–6 map one-to-one onto the skill suite. That self-consistency exists nowhere in the
article, and it is what makes doctrine+tooling fixes *one* coherent move rather than two.

## Verdict (one paragraph)

Measured against the article: **ahead** on doctrine, transmission, and decision discipline; **at
parity** on verification intent and on raw throughput (session-level fan-out at 5–10 matches the
article's "running 3–10 parallel agents is a given"); **behind** on codifying that parallelism,
protecting shared repos from it, unattended work, independent redundancy in verification, model
allocation, and prompt-debt hygiene. The binding constraint is not parallelism — it is that **the
harness does not know it is being run in parallel**, so it cannot protect concurrent runs from each
other, and the handbook cannot teach the practice to the people meant to inherit it.

Of those, model allocation is now closed
([ADR-0012](adr/0012-inherit-the-session-model-on-reasoning-agents.md)) and the security-scanning gap
turned out not to be one ([ADR-0013](adr/0013-scan-for-security-on-cadence-not-per-change.md)).

---

## Corrections — retracted claims (do not resurrect these)

- **RETRACTED: "no fan-out / serialising caps throughput at one."** Wrong. Fan-out exists,
  human-orchestrated at the session level (5–10 parallel sessions); each `AskUserQuestion` gate is a
  multiplexing point, not a throughput block. The lead's attention is the *scheduler* — exactly the
  article's model, with the cost the article itself names (Katelyn: context switching easier, still
  hard). What survives is narrower: the practice is *uncodified*, *unsafe on shared repos*, and
  *attended-only* — items A3, B1, A5 below.
- **RETRACTED (first-pass reading): "cap-at-2 loops are a token-budget artefact."** The handbook's
  "retry loops" failure mode independently says *if a fix fails twice, stop and reassess — the framing
  is usually wrong*. Doctrine and automation agree. Keep the caps. But note the system **conflates
  retries with redundancy** — an independent fresh-context second opinion is not a retry (item A4).
  **Update (26 Aug 2026)**: the *keep the caps* half is itself now overturned by operating evidence. The
  3→2 cut was in fact a `perf` commit (`6d6c333`), and at the gate the lead answered `Continue
  iterating` in substantially every case, so budgets went back to three in
  [ADR-0014](adr/0014-raise-correction-loop-budgets-to-three-passes.md). The conflation point stands.
- **RETRACTED: "A2 is small — closer to an oversight."** Wrong. The three scanners are whole-repo
  (`git ls-files`), never diff-scoped, so per-implementation runs cost the same on a one-line fix as on
  a large feature *and* re-report the same pre-existing findings every time. Their absence from the
  pipeline is a design boundary, not an oversight. Full reasoning and the deferral decision in
  [ADR-0013](adr/0013-scan-for-security-on-cadence-not-per-change.md).
- The remaining budget-driven gaps (uniform sonnet, no unattended lane) trace to one constraint the
  article says does not apply at Anthropic: **a token budget**. Break it deliberately in one or two
  places, not uniformly. The model half of this is now decided
  ([ADR-0012](adr/0012-inherit-the-session-model-on-reasoning-agents.md)); the unattended half is A5.

---

## Open backlog — Track A: tooling

*(A1 and A2 are closed. See [ADR-0012](adr/0012-inherit-the-session-model-on-reasoning-agents.md) and
[ADR-0013](adr/0013-scan-for-security-on-cadence-not-per-change.md). Numbering is retained so earlier
notes still resolve.)*

### A3. Make same-repo parallel sessions safe *(small→medium — practice already violates assumptions)*

Two `/project-implement` runs in one repo **see each other's edits**: every verification agent scopes
itself by `git diff` + untracked files, so session B's half-finished work lands in session A's
test-writer and reviewer scope; the Phase 4 checkpoint (`git add -A` via temp index) snapshots the
*union* of both sessions and a recovery restore would resurrect the other session's WIP; inline test
runs execute against a tree containing the other session's changes. This is Katelyn's "agents stepping
on each other's toes", verbatim. Worktrees were already tried and reverted (`407227c`; Jarred also
found them slow) — his alternative was orchestrator-owns-writes.
**Move (cheapest honest fix)**: a stated rule — *parallel sessions on one repo must own disjoint
paths* — plus optionally a per-run scope declaration the diff-based agents filter against.
**Open**: where does the scope declaration live (argument, `.claude/` file, env)?

### A4. Add independent redundancy where it pays *(medium)*

Distinct from retry-loop depth (raised to three by
[ADR-0014](adr/0014-raise-correction-loop-budgets-to-three-passes.md); more passes of the same shape
is not redundancy). Redundancy = a fresh-context independent
pass that catches what the first *structurally* couldn't see. Article: two AI reviewers arguing on the
PR, 11 scanner runs, fresh-context blast-radius judges. Today: every reviewer runs exactly once.
**Move (options, pick one to trial)**: a second fresh-context design review on full mode; scanner
re-run after correction loops; an adversarial verify pass on reviewer findings.
**Bound**: redundancy only where an oracle or a cheap judge exists — don't double-spend on prose.

### A5. Unattended lane experiment *(medium — the accurate half of the retracted fan-out claim)*

5–10 attended sessions still all need the lead present; nothing runs from an issue, overnight, or
while away — the article's "agents running in the background or cloud" half. The article's closest
analogue to Rise is **Bun: a small team with a wide surface** (~14 Rise repos), and their answer to
that ratio was issue → repro container → fix container → PR, auto-rejected without a test.
**Move**: one GitHub Action running Claude on issue/PR events, in **one** repo, as an experiment — not
a plugin skill until it earns its place. **Bound**: propose-PR only, never merge; needs a PR landing
convention while attended work stays direct-to-main
([ADR-0009](adr/0009-commit-direct-to-main.md) is coupled to this).
**Trust bound (from the handbook)**: unattended output is only admissible where an oracle other than a
reading human judges correctness — a trusted suite, a spec, a mechanical transformation. Jarred's
64-agent rewrite qualified precisely because Bun's language-independent test suite was the oracle.
Needs the tiered trust model in B2 to exist first
([ADR-0007](adr/0007-line-level-defensibility-as-the-default.md) currently forbids it).

## Open backlog — Track B: doctrine / way of working

> These edit the engineering handbook and `/project-coach`, which live in `it--claude-rise-plugin`,
> **not** in this repo.

### B1. Codify the parallel-session practice — the distillation gap *(the biggest-leverage doctrine edit)*

The most Anthropic-like part of the actual practice (5–10 parallel sessions) appears **nowhere** in
the handbook, coach, or rules. Handbook §0 teaches "an AI at your side" — singular, serial. Juniors
are distilling how the lead worked in 2025, not how the lead works now; and when tooling moves (A3,
A5), the handbook must move in the same commit or the distillation loop propagates the old model.
**Move**: rewrite handbook §0 around the multi-session reality — what parallelises (independent,
oracle-checkable work) vs what doesn't (design, exploration); how to scope sessions so they don't
collide (ties to A3); how to review N concurrent outcomes; the context-switching cost (the article
names it honestly). Make `/project-coach` aware of it.

### B2. Add a tiered trust model to handbook §0 *(keeps the junior default, names the boundary)*

"I can explain and defend every line" stays the default — but it currently has **no escape valve**,
and it outright forbids work like the Bun rewrite (mechanical bulk change, oracle-verified, nobody
reads 500K lines). The hinge is already written in handbook §1.2: *"reviewability comes from
legibility, not size."*
**Move**: two named tiers — line-level defensibility for hand-directed feature work; **oracle-level**
defensibility for mechanical/bulk work, with qualifying gates listed (trusted suite + automated
review + scanners). Explicitly *not* a licence to skim feature work.
**Note**: this is the named-boundary half of
[ADR-0007](adr/0007-line-level-defensibility-as-the-default.md); landing it amends that ADR.

### B3. Promote testing from a checkbox to a section *(doctrine lags the tooling here)*

The handbook has one checklist line ("tests pass, and I added/updated tests"). The tooling already
encodes fails-before/passes-after (RED→GREEN for governed layers,
[ADR-0003](adr/0003-enforce-red-green-on-governed-layers.md)) — **the doctrine never teaches it**.
And handbook §2.6's "invite others" implies human reviewers only: a junior reading it wouldn't know
the AI reviewer agents exist — a seam between the two plugins, not a missing capability.
**Move**: a testing section teaching the fail-first proof, and a review step that names the automated
reviewers as the pass *before* "invite others".

### B4. Legitimise the spike *(the word appears nowhere in the doctrine)*

Handbook §2.1 keeps understanding strictly read-only; Katelyn says the opposite is now the fast path
(*"prototyping itself was more about understanding the requirements"*; stub service + shadow traffic,
interfaces ironed out while building underneath). Throwaway code is the thing AI made nearly free.
**Move**: add the spike as a deliberate, disposable mode — with the guard that spikes are deleted,
never silently promoted (that guard is *why* it was left out for juniors; write it down instead).

### B5. Single-source the triple-encoded doctrine *(maintenance — drift is already observable)*

The same principles live in `rules/general.md`, two handbook variants, and agent constraint blocks —
synchronised by memory. Observed drift: the `.claude.md` handbook variant has the full "catch
yourself" list which the human variant lacks; the human variant has richer §1.2 (dead-code
discipline, the legibility argument) and a §9 rule the AI variant drops (*"infrastructure changes
deploy through CI, not by hand"*); ~~the plugin `CLAUDE.md` says 18 skills / 16 agents — actual counts
are 19 / 14~~ **(done 2026-08-07 — counts corrected to 19 / 14)**.
**Move**: decide the single source; generate or checklist-verify the derived copies.

## Open backlog — Track C: recurring ritual

### C1. Prompt-debt ritual per model generation

`project-implement` is a ~300-line state machine (nested loop counters, a shared max-2 budget across
two sub-loops, five RED/GREEN verdict cases, `commit-tree` plumbing) — four months of steadily
accumulating determinism. Thariq deleted **80%** of the Claude Code system prompt because the model
got smarter: *"you have to revisit any assumptions you have made because it can change with a new
model generation."* Determinism stays
([ADR-0010](adr/0010-keep-skills-deterministic-state-machines.md)) — but it must be re-earned per
generation, and that ADR is explicitly **conditional on this ritual running**.
**Move**: on each model generation, halve the biggest skill, run both versions against the same
requirement, compare, keep the cut if it holds.

---

## Decided elsewhere

Everything the review validated, deliberately diverged on, or excluded is now an ADR. See
[`adr/README.md`](adr/README.md) for the index. In particular:

- What holds up and should not be touched →
  ADRs [0001](adr/0001-manufacture-judgment-through-codified-doctrine.md),
  [0002](adr/0002-weight-the-pipeline-toward-verification.md),
  [0003](adr/0003-enforce-red-green-on-governed-layers.md),
  [0004](adr/0004-scale-planning-rigour-to-complexity.md),
  [0005](adr/0005-inject-an-explicit-failure-modes-list.md),
  [0006](adr/0006-compound-solved-problems-into-skills.md)
- Deliberate divergences from the article →
  ADRs [0007](adr/0007-line-level-defensibility-as-the-default.md),
  [0008](adr/0008-gate-every-mutating-phase-on-a-human.md),
  [0009](adr/0009-commit-direct-to-main.md),
  [0010](adr/0010-keep-skills-deterministic-state-machines.md)
- Considered and excluded → PR-flow-at-scale in [ADR-0009](adr/0009-commit-direct-to-main.md),
  fuzzing in [ADR-0002](adr/0002-weight-the-pipeline-toward-verification.md),
  HTML reports in [ADR-0011](adr/0011-author-reports-in-markdown.md)
- Team-shape findings (two-pizza, max-2-per-project) — no mapping to a solo-lead portfolio. Out of
  scope rather than rejected; noted in [`adr/README.md`](adr/README.md).
