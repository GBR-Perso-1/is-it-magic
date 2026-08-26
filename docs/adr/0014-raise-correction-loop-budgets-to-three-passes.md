# 0014. Raise correction-loop budgets to three passes

**Status**: Accepted
**Date**: 2026-08-26

## Context

Every correction loop in `project-implement` was capped at two iterations. The cap came from two
places. [ADR-0005](0005-inject-an-explicit-failure-modes-list.md) encodes the failure-mode heuristic
that if a fix fails twice you should stop and reassess, because the framing is usually wrong. Commit
`6d6c333` (12 May 2026) then cut the ceilings from three to two as a cost measure, bundled with the
developer's inline smoke run and with skipping reviewers that had already passed.

Operating evidence has not matched the prediction. The gate fires frequently and the lead answers
`Continue iterating` in substantially all cases. A gate overridden that reliably is not supplying
judgment; it is charging a context switch for a decision already taken. Under
[ADR-0008](0008-gate-every-mutating-phase-on-a-human.md) the gates are also the scheduling points
across five to ten parallel sessions, so a gate that resolves the same way every time is scheduler
noise rather than control. The shift toward longer autonomous runs compounds the cost.

The apparent conflict with ADR-0005 is a confusion of scale. The rule in `rules/general.md` addresses
an agent retrying variations of the same fix inside one attempt. A pipeline iteration is not that: a
fresh test-writer re-derives scenarios from the requirements, and the developer receives findings it
did not previously hold. Two rounds is the right ceiling for the first case and was never established
for the second.

## Decision

Raise every correction loop in `project-implement` from two iterations to three.

- The dev-to-test loop, in full mode and in increment mode.
- The GREEN dev-to-test budget on the test-first path, including the `OTHER_FILES` fix cycles that
  share that budget.
- The full review loop.

Two budgets deliberately do not move.

- The scaffold-defect sub-loop stays at two attempts. It is not a correction loop over behaviour but
  a mechanical repair of stub signatures. Signatures wrong twice means the plan is wrong, which is
  the genuine reframe case, and its fallback already offers to abandon test-first rather than retry.
- `rules/general.md` keeps "if a fix fails twice, stop and re-frame". It governs the agent scale, not
  the pipeline scale, and holding those apart is the substance of this record.

## Consequences

- Worst-case token cost per gated loop rises by roughly half. That is the explicit price of a gate
  the lead was otherwise paying for in attention.
- [ADR-0002](0002-weight-the-pipeline-toward-verification.md) names `test-writer` the pipeline's
  largest cost multiplier, because it is spawned fresh on every iteration with no context reuse. That
  multiplier is now three rather than two, which sharpens rather than weakens the reason it stays
  pinned to a cheaper model. The same record's claim that roughly six of eight agent slots verify
  moves further toward verification, which is the direction it argues for.
- The review loop is the expensive end of that. [ADR-0012](0012-inherit-the-session-model-on-reasoning-agents.md)
  unpinned the reviewers to the session model on the argument that they are diff-scoped, single-pass
  and capped at two runs. One of those three bounds has now loosened, so the worst case there is
  three Opus-class review rounds rather than two. The mitigation already in the skill is that only
  reviewers which flagged issues are re-spawned, so the third round is rarely the full set.
- The escalation is unchanged in kind. Exhaustion still opens `AskUserQuestion` with `Continue
  iterating` offered first, so the number decides when the question is asked and never whether work
  is allowed to continue.
- If the third pass proves to resolve as reliably as the second did, the cap is still mis-tuned and
  the answer is not four. It is to make the additional pass structurally different from the ones
  before it, which is backlog item A4 rather than a further increment here.
- The loop-budget statements in ADR-0002, ADR-0003, ADR-0005, ADR-0008 and ADR-0012 are amended by
  this record. Their reasoning stands as written; only the number changes.
- A4's premise that retry caps stay because doctrine backs them no longer holds unqualified. The item
  survives, because independent redundancy and additional depth remain different things.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0003](0003-enforce-red-green-on-governed-layers.md),
[ADR-0005](0005-inject-an-explicit-failure-modes-list.md),
[ADR-0008](0008-gate-every-mutating-phase-on-a-human.md),
[ADR-0012](0012-inherit-the-session-model-on-reasoning-agents.md)
