# 0018. Re-verify proportionally on the design-error path

**Status**: Accepted
**Date**: 2026-08-31
**Amends**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md)

## Context

[ADR-0017](0017-loop-only-on-violations.md) fixed what may start a review-loop round — only a
Violation — but not what a round then costs. The design-error path still read "Re-run from Phase 2
with the revised plan and all reviewers reset", so every design correction re-ran developer,
test-writer, and all three reviewers regardless of how small the revision was. The 50-minute run
measured in ADR-0017 paid that five-agent price three times over for what was, in the end, a 35-line
change. Deciding what a delta actually invalidates needs per-reviewer scope the orchestrator can read
deterministically ([ADR-0010](0010-keep-skills-deterministic-state-machines.md)); reviewer reports
carried only a file count, not a file list, so the three reviewer templates are amended alongside this
record to emit the list.

## Decision

On the design-error path, the architect's revision returns a **Design Correction**, and the round that
follows re-verifies only what it invalidates:

- A **fresh developer agent** ([ADR-0016](0016-bound-the-developer-per-gate-run-and-per-review-round.md))
  applies the Design Correction against the plan. Its **Changes Made** file list is this round's
  **delta** — the scope the rest of the round reasons about.
- Phase 3 (testing) re-runs unless the delta is docs/config-only under step 8's relevance test **and**
  the developer's report is clean. In that case the previous round's test results stand and Phase 3 is
  skipped for this round.
- Reviewers that previously flagged Violations always re-run. In addition, any previously-passed
  reviewer whose verdict is now **stale** re-runs: a passed verdict is stale iff the delta's file list
  intersects the file list in that reviewer's own report (`**Files reviewed**` / `**Files analysed**`),
  or the delta contains a file that appears in no reviewer's most recent report (a file new this
  round). Step 8's relevance test is also re-applied to the delta, so a reviewer the previous round
  skipped — the performance reviewer on a docs/config-only round — is spawned when the Design
  Correction introduces the run's first runtime code; without this, a stale-or-flagged rule alone
  could never reach a reviewer that had produced no verdict to go stale. A passed reviewer that is
  not stale is not re-spawned. Whenever the quality reviewer runs at all, it still runs alone and
  first, unchanged from the existing ordering.

The implementation-error path is unchanged: its delta is already bounded to the flagged findings, so
the existing "re-run only reviewers that flagged Violations, skip the rest" rule already fits it. A
design revision is different in kind — it can move work into files no passed reviewer ever saw — which
is why the stale-verdict rule applies to the design path only.

ADR-0014's three-pass budgets and the RED→GREEN policy are unchanged by this record. This amends
ADR-0014 by reducing what a round costs, not by changing how many rounds may run.

**Recorded alongside**: the three reviewer report templates are amended twice in answer to the same
measured run, and both changes are recorded here rather than in separate records. First, the
file-count header lines (`**Files reviewed**`, `**Files analysed**`) now also emit the reviewed file
list — this is what makes the stale-verdict rule above readable at all, since without a list the
orchestrator has nothing to intersect the delta against. Second, the severity definitions are
tightened so that a Warning must state a concrete failure scenario (the input or state that triggers
it, and the wrong outcome that results); a finding without one is a Suggestion, and Violations remain
reserved for defects, requirement-coverage gaps, or rule breaches. This closes the follow-up ADR-0017
left open on requiring Warning evidence.

## Consequences

- A docs/config-only delta drops the test-writer for that round — ADR-0002's "spawned fresh every
  iteration" is now conditional on this path, rather than absolute.
- Because reviewers scope their reports to the whole working-tree diff at the time they ran, a delta
  confined to files already touched earlier in the run intersects every passed reviewer's file list,
  so they all re-run regardless. The saving from this record concentrates in two cases: where a
  reviewer's reported scope was narrower than the full diff, and where the delta is docs/config-only.
  This is accepted — a passed verdict over a file the revision rewrote is stale in fact
  ([ADR-0002](0002-weight-the-pipeline-toward-verification.md)), and the rule is deliberately
  conservative about when it may skip a reviewer.
- ADR-0016's description of the design-error path as "re-entry at Phase 2" is superseded by the direct
  fresh developer spawn described above; the one-developer-per-round principle it established is
  unchanged.
- This closes ADR-0016's reader gap: Phase 3's first bullet now reads a red **Build / Verify Status**
  or an exhausted fix budget whether or not an inline test run happened, and the Draft and Quick mode
  summaries surface a red developer report explicitly. An explicit read of **Deviations from Plan** as
  such at Phase 2 step 5 remains a follow-up, as ADR-0016 already noted.
- The `TEST_FIRST_ACTIVE=true` gap ADR-0016 left open is unchanged by this record.
- A third pre-existing gap joins ADR-0016's two as a follow-up, unfixed here: on the Increment
  "Promote to full" path, a step-11 design error says "pass findings back to the **architect
  agent**", but no architect instance exists on that path — the design-error route is unreachable
  there without first spawning an architect, which no bullet currently does.

## Alternatives considered

**Lens-based staleness** — classify each reviewer's concern as a fixed set of file "lenses" rather than
reading its reported file list. Rejected: once reports carry an actual file list, a fixed lens saves
nothing the intersection test does not already give, while adding a coarse proxy for a scope the report
already declares precisely.

**Stale iff the delta touches a file the reviewer raised a finding on**, rather than any file in its
reported scope. Rejected: a reviewer that passed cleanly raised no findings at all, so a clean pass
could never go stale under this rule even when the delta rewrites a file it reviewed — against
[ADR-0002](0002-weight-the-pipeline-toward-verification.md)'s weighting of the pipeline toward
verification.

**Apply the stale-verdict rule to the implementation-error path too.** Rejected: that path's delta is
already bounded to the flagged findings, so the existing "flagged-only" rule already fits it without
the added machinery.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0010](0010-keep-skills-deterministic-state-machines.md),
[ADR-0016](0016-bound-the-developer-per-gate-run-and-per-review-round.md),
[ADR-0017](0017-loop-only-on-violations.md)
