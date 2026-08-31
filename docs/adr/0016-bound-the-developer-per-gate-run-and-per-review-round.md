# 0016. Bound the developer per gate run and per review round

**Status**: Accepted
**Date**: 2026-08-28
**Amended by**: [ADR-0018](0018-re-verify-proportionally.md)

## Context

Thirty days of transcripts on the main machine (de-duplicated by request, scanned on 28 August 2026 with
`docs/investigations/token-usage-scan.py`; scan output not committed) measure the `developer` agent at
50% of all suite tokens. Of 135 runs, 21 exceeded 200 turns and carry 69% of the developer's tokens
between them. 51 runs peaked above 200k of context, 16 above 400k, one as high as 875k, and none
compacted. Since 26 August, 49% of developer runs were continued via `SendMessage` more than twice — the
orchestrator drives one developer instance through successive fix rounds, so its context ratchets with no
reset point.

The shape of the long runs is not deep reasoning; it is a one-edit/one-build/one-re-read loop. One
638-turn run recorded 259 Bash calls, 160 Reads, 132 Edits, `dotnet build` run nine times, `npm test`
run nine times, and a single file edited nine times and read back five times. Per-turn model speed is
unchanged across the period — the cost is turn count, not latency.

Before this record, the agent's only brake against that loop was `rules/general.md`'s "if a fix fails
twice, stop and re-frame", which [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md)
already identifies as an agent-scale rule, distinct from the pipeline-scale loop budgets that record
raised to three. `agents/developer.md` never carried that discipline in its own constraint block, even
though [ADR-0005](0005-inject-an-explicit-failure-modes-list.md) wants pipeline agents to hold their
failure-mode guidance explicitly in context rather than relying on it being inherited from a rules file
the agent may or may not read closely. Separately, Phase 3 of `developer.md` read "fix any build/compile
errors before reporting completion" — an unbounded instruction with no exit condition, which is exactly
what a nine-build, nine-edit loop looks like when followed literally.

## Decision

Apply two bounds, at the two scales ADR-0014 already distinguishes.

**Agent scale**, added to `agents/developer.md`'s own constraints so the agent carries the discipline
itself rather than depending on the orchestrator or an inherited rules file:

- Batch every edit the plan calls for before running the gate. The gate — the agent's Phase 3 check
  plus any inline test run the skill requests — runs after all edits, never after a single edit or a
  single step; the only re-runs are the capped fix attempts. On a correction round the findings are
  the work list and the same rule applies.
- Never re-read a file already held in context from this run's own reads or edits — only re-read when a
  tool other than the agent's own edits may have changed it.
- Cap the fix-verify cycle at two fix attempts per run, where a run is one spawn or one `SendMessage`
  continuation and each starts a fresh budget. Every attempt applies every outstanding error as one
  batch. A gate still red after the second attempt is left as-is, with the failure recorded under
  **Deviations from Plan**, and the agent returns rather than continuing to grind.

**Pipeline scale**, added to `skills/project-implement/SKILL.md`: a developer instance now lives for one
review round. Both Phase 4 correction paths spawn a fresh developer rather than continuing the previous
one via `SendMessage` — the "implementation errors only" path directly, the "design errors" path through
its re-entry at Phase 2 with the revised plan — and both carry forward the plan (or the implementation
brief on the no-plan promotion path), the original requirements, the findings, and the Implementation
Reports of every previous instance in the run (the first covers the implementation, later ones only their
round's corrections; together they are the state the new instance needs, and `developer.md` reads them as
a signal that the tree is already implemented). Within a single round — Phase 3's single inline-fix
continuation, the dev↔test loop, and the RED→GREEN sub-flow's steps (b) to (e), of which (c) and (d)
explicitly require "the same developer agent" — `SendMessage` continues to address the same instance as
before; only the boundary between review rounds gets a reset.

## Consequences

- Exhaustion of the fix budget reaches the orchestrator through Phase 3's first bullet, which is the
  one point where a red developer report is read. That bullet sends the failures back exactly once —
  a single `SendMessage` continuation, which is a new run with its own two-attempt budget — and then
  spawns the test-writer regardless of what the continuation returned. Anything still failing enters
  the dev↔test loop's max-3 budget as a counted iteration, rather than a second inline continuation.
  Before this record that bullet had no bound; it did not need one, because a developer rarely returned
  red. As first written, that read was also conditional on an inline run having happened, so a red
  report arriving via Draft promotion (no inline run), or ending a Draft or Quick run, had no reader;
  [ADR-0018](0018-re-verify-proportionally.md) closes that gap. The orchestrator still does not read
  **Deviations from Plan** as such at Phase 2 step 5; an explicit read there remains a follow-up.
- A fresh developer per review round pays a bounded re-orientation cost — reading the plan, requirements
  and prior report again — in place of the unbounded context ratchet a continued instance was
  accumulating across rounds. That cost is real but fixed, unlike the ratchet it replaces.
- This is a first step toward ADR-0014's backlog item A4 ("make the additional pass structurally
  different from the ones before it"), applied here to the developer specifically, without closing A4
  for the rest of the pipeline.
- ADR-0014's loop budgets (three for the dev↔test loop, three for the review loop, two for the
  scaffold-defect sub-loop) are unchanged; this record bounds turns within a gate run and instances
  across rounds, not the count of rounds itself.
- **Deviations from Plan** now carries two meanings: a genuine plan/reality mismatch, as before, and a
  fix budget exhausted on an otherwise valid step. Nothing in the orchestrator distinguishes them today;
  both reach it only through the indirect path above. The follow-up named there is what would make the
  distinction actionable.
- Two pre-existing gaps in `project-implement` are exposed but not closed here, and are follow-ups: on
  the Increment "Promote to full" path a step-11 correction re-runs Phase 3, whose test-writer bullet
  requires the plan's Test Strategy section that this path never had; and on a `TEST_FIRST_ACTIVE = true`
  run Phase 3 has no inline-run bullet, so the inline smoke check step 11 asks the fresh developer for
  has no reader there and the re-run goes straight to RED confirmation against an implemented tree.

## Alternatives considered

**Fresh spawn after N `SendMessage` continuations, counted generically.** Rejected: a fixed
continuation count can fire in the middle of the RED→GREEN sub-flow, between step (c)'s scaffold-defect
correction and step (d)'s GREEN implementation, both of which require the same instance by design. A
count-based reset does not know about that boundary; a round-based one does.

**An in-agent turn budget the developer enforces on itself.** Rejected: the agent cannot count its own
turns reliably from inside a single run, and the actual waste is not turn count in the abstract but the
specific one-edit/one-build/one-re-read loop shape — capping fix attempts and batching edits addresses
the shape directly, where a turn counter would not.

**A context cap or forced compaction inside the developer's run.** Rejected: the measured lever is turns,
not context size — per-turn model speed is unchanged across the period, so a context cap saves
comparatively little next to cutting the number of gate round-trips.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0005](0005-inject-an-explicit-failure-modes-list.md),
[ADR-0010](0010-keep-skills-deterministic-state-machines.md),
[ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md)
