# Decision 0001: V1 scope and architecture

## Status

Accepted

## Context

The project must be:

- portfolio-ready
- practical for one developer
- clearly agentic (state, planning, adaptation, tool/data usage)

## Decision

V1 uses:

- FastAPI + SQLite for fast backend iteration and persistent state
- Next.js App Router + Tailwind for a polished but maintainable frontend
- retrieval-grounded chat from markdown onboarding corpus
- deterministic blocker and escalation logic from structured playbooks/contacts

## Rationale

- fastest path to an end-to-end working system
- clear demonstration of agentic workflow behavior
- design allows later swap to richer LLM orchestration without rewriting core product flows

## Consequences

### Positive

- strong demo narrative with visible business relevance
- deterministic behavior for tests and interview walkthroughs
- modular service boundaries for future enhancement

### Tradeoff

- retrieval quality is baseline (TF-IDF), not production-grade semantic embeddings
- no auth/multi-tenant setup in V1

