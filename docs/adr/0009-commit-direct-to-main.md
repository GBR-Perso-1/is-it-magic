# 0009. Commit direct to main, no PR machinery

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)

## Context

Pull requests exist to coordinate review across people who are not in the same head. The source
article describes an environment where that coordination problem is severe: over a hundred pull
requests a day flowing between many humans and several competing AI reviewers.

These repositories have one or two humans each. The review that matters already happened, inline, in
the session that produced the change.

## Decision

Commit directly to `main`. Do not require branches or pull requests for ordinary work.

Commits may span multiple concerns rather than being artificially split. Conventional commit format
(`type(scope): description`) is required regardless, so history stays readable without PR titles doing
that job.

Project-level rules override this where a project's own branching policy requires otherwise, and the
handbook parameterises it as "follow the project's branching policy" rather than hard-coding
direct-to-main.

## Consequences

- No ceremony that only exists to serve a coordination problem this context does not have.
- Review quality depends entirely on the in-session reviewers and the human gate, since there is no
  second checkpoint after the fact.
- An unattended lane would need somewhere to land its output, and direct-to-main is not it. This
  decision is therefore coupled to backlog item A5: if unattended work is ever adopted, it needs a PR
  landing convention while attended work continues direct to main.

## Alternatives considered

**PR-based flow with competing AI reviewers at scale**, as described in the source article, where two
AI reviewers argue on the pull request and a third-party reviewer competes with them. Rejected: it
exists to coordinate volume across many actors, which is not the binding constraint here. Revisit only
if backlog item A5 lands and unattended changes start arriving as pull requests.

## Relates to

[ADR-0008](0008-gate-every-mutating-phase-on-a-human.md)
