# 0017. Loop only on violations

**Status**: Accepted
**Date**: 2026-08-28
**Amends**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md)

## Context

A design review on a single change was measured today running Warnings three rounds in a row, at
decreasing weight (5 findings, then 3, then 1), with no Violation present in any round. Each round
re-ran the full five-agent review-loop iteration regardless, because `project-implement`'s Phase 4
step 11 looped on "no violations or warnings" as a single gate. The run took 50 minutes; rounds 2 and
3 alone accounted for 32 of those minutes, chasing findings that were never blocking in the first
place. An 18-minute run became a 50-minute one for a change the design reviewer never actually
rejected.

## Decision

Split the Phase 4 gate by severity. Only a **Violation** — a reviewer finding marked Violation, or a
requirement-coverage failure or missing functionality reported by the design reviewer — re-enters the
review loop. Warnings and Suggestions never trigger a loop-back; they are collected across all
reviewers into a **review follow-up list** (file:line, one-line finding, the reviewer's
recommendation) and carried to the Phase 5 summary, where the user sees them at the commit gate and
may accept them or deliberately re-invoke review.

The three loop budgets ADR-0014 raised to three passes are unchanged. That record bounded how many
rounds a loop may run; this one bounds what is allowed to start a round in the first place. Amending
rather than reversing ADR-0014 reflects that distinction.

## Consequences

- A Warning-grade design gap can now ship without a further review round unless the user actively
  sends it back. This is accepted: the user sees the follow-up list before the commit gate, so the
  decision moves to the point where it is cheapest to make rather than being spent automatically on
  every round.
- Reviewer severity labelling becomes load-bearing in a way it was not before — a finding mislabelled
  as Warning when it is really a Violation now ships silently rather than looping. A follow-up is to
  require Warnings to state a concrete failure scenario, so the label carries enough evidence to be
  checked.
- Measured cost avoided: the three-round case above would have stopped after round 1 under this gate,
  saving the 32 minutes and ten of the fifteen agent runs spent on rounds 2 and 3.

## Alternatives considered

**Proportional re-verification** — re-run only the reviewers that flagged Warnings on the design path,
rather than the full five-agent set, instead of removing the loop trigger. Deferred as complementary:
it would reduce the cost of a Warning-triggered round but does not address that most Warning rounds
resolve to the same finding at decreasing weight without ever becoming blocking.

**Roll the review-loop budget back from three to two.** Rejected: that changes the ceiling on how many
rounds run, not the trigger that starts one. The measured case reached round 3 only because every
round re-triggered on Warnings; a lower ceiling would have truncated the run rather than fixed the
cause.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0010](0010-keep-skills-deterministic-state-machines.md),
[ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md),
[ADR-0016](0016-bound-the-developer-per-gate-run-and-per-review-round.md)
