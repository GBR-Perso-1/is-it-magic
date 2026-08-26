# 0011. Author reports in Markdown, not HTML

**Status**: Accepted
**Date**: 2026-08-07

## Context

Reports produced by this system (archaeology reports, security scans, investigation findings) could be
authored as HTML instead of Markdown. The source article records a preference for exactly that: HTML
output is richer, renders consistently, and is easier to share with people who will not open a
repository.

The counter-pressure is a standing operator rule that all working documents are Markdown, with
conversion to other formats only on explicit request.

## Decision

Keep Markdown as the authoring format for all reports and working documents.

## Consequences

- Reports stay diffable, greppable, and reviewable in the same tools as the code they describe, which
  matters because they are written into the repository rather than sent somewhere.
- Reports are less immediately shareable with a non-engineering audience. Conversion remains available
  on request, so this is a default rather than a prohibition.
- This is recorded as a preference decision rather than an engineering gap. It was considered during
  the source-article review and deliberately not treated as something to fix.
