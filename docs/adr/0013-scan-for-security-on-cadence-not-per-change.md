# 0013. Scan for security on cadence, not per change

**Status**: Accepted
**Date**: 2026-08-07

## Context

`repo-security-scan` owns three parallel scanner agents that `project-implement` never calls, so
security review is opt-in on a pipeline that reviews quality, design and performance automatically.
The source article contrasts sharply here, describing eleven scanner runs on a single rewrite with
verification default-on and repeated.

This looked like an oversight worth a small fix: spawn the three scanners from the review phase
alongside design and performance, since they are read-only and compose with the existing rule that the
mutating reviewer runs alone first.

Inspecting the agents showed the framing was wrong. All three resolve scope identically, via
`git ls-files` inside `SCAN_ROOT` (`agents/scanner-secrets.md:40`, `agents/scanner-injection.md:34`,
`agents/scanner-exposure.md:33`). **None is diff-scoped.** They were built for an on-demand whole-repo
audit, so their absence from the pipeline is a design boundary rather than an omission.

Wiring them in unchanged would be net-negative on two counts:

- **Cost would not track the work.** A one-line fix pays the same three full-tree sweeps as a large
  feature, each running up to twenty grep patterns, with `scanner-exposure` reading every
  configuration file in full. Unlike `developer` and `test-writer`, the spend is constant. Multiply by
  five to ten parallel sessions.
- **Output would be near-identical every run.** Scanning the tree rather than the change re-reports
  every pre-existing finding on every implementation, and no baseline or delta suppression exists in
  the finding schema. That is the standard path to alert fatigue: the control decays into noise, and
  then it is not a control.

The article's eleven scanner runs were on a 500,000-line rewrite where the scanned surface genuinely
changed wholesale between runs. It does not transfer to a forty-line change.

## Decision

Do not wire the scanners into `project-implement`. Keep `/repo-security-scan` opt-in and run it on a
**cadence**: before a release, after dependency upgrades, and periodically. Whole-repo scope is correct
for that job.

## Consequences

- Security coverage stays genuine, because findings are read rather than skimmed past.
- A secret introduced by a change is not caught before it is committed. That specific gap is the one
  thing per-change scanning would be good at, and it is knowingly accepted.
- Cadence discipline is now a human responsibility with no automation enforcing it.

## Alternatives considered

**Make the scanners diff-aware, then wire them in.** Give them a scope input resolving from
`git diff --name-only HEAD` plus untracked files instead of `git ls-files`. Cost would then track the
change and findings would concern code just written. This is the version worth having, and it remains
open for later. It is medium effort rather than small: a scope-resolution rewrite in all three agents
plus the pipeline wiring, and it leaves two questions open, namely whether it applies to increment mode
as well as full, and whether findings route to the developer or gate to the user. **Bound**: doing this
without the diff-scoping is worse than not doing it at all.

**Fire the scanners only when the diff touches risk surface** such as auth, configuration, SQL, HTTP
handlers or environment files. Requires no scanner changes, but still pays whole-repo cost whenever it
fires.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0012](0012-inherit-the-session-model-on-reasoning-agents.md)
