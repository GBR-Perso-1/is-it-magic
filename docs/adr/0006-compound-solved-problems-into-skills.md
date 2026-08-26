# 0006. Compound solved problems into skills

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)

## Context

A problem solved once in a session is normally lost when the session ends. The next person, or the
same person on another repo, rediscovers it. The source article's compounding mechanisms operate at CI
level: automations that catch a class of regression once it has been characterised.

Compounding at CI level catches recurrences. It does not transfer the knowledge of how the problem was
solved.

## Decision

Provide `session-to-skill`: a skill that retroactively distils completed work from the current session
into a reusable `fix-` or `migrate-` skill, scoped by a natural-language direction describing which
part of the session to capture.

The output is a versioned, installable artefact, not a note. It is executable by anyone who installs
the plugin.

## Consequences

- Compounding happens at knowledge level rather than only at regression level. The loop demonstrably
  runs: `fix-openapi-enum-schema` and `migrate-navigation-to-static` in the Rise plugin are its
  visible outputs.
- The skill count grows over time, which is intended, but it means skill discovery and naming
  discipline matter more as the suite widens.
- Distilled skills encode the practice as it stood when they were written, so they inherit whatever
  was true then. This is the same ossification risk that
  [ADR-0010](0010-keep-skills-deterministic-state-machines.md) addresses for the core skills.

## Relates to

[ADR-0001](0001-manufacture-judgment-through-codified-doctrine.md),
[ADR-0010](0010-keep-skills-deterministic-state-machines.md)
