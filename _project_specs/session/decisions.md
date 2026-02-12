<!--
LOG DECISIONS WHEN:
- Choosing between architectural approaches
- Selecting libraries or tools
- Making security-related choices
- Deviating from standard patterns

This is append-only. Never delete entries.
-->

# Decision Log

Track key architectural and implementation decisions.

## Format
```
## [YYYY-MM-DD] Decision Title

**Decision**: What was decided
**Context**: Why this decision was needed
**Options Considered**: What alternatives existed
**Choice**: Which option was chosen
**Reasoning**: Why this choice was made
**Trade-offs**: What we gave up
**References**: Related code/docs
```

---

## [2026-02-12] Initial Project Setup - Full Stack with Claude Skills

**Decision**: Full setup with skills, guardrails, CI/CD, and agent teams
**Context**: Existing codebase had no development tooling, linting, testing, or CI/CD
**Options Considered**: Skills only, skills + guardrails, full setup
**Choice**: Full setup
**Reasoning**: Project needs proper development infrastructure for maintainability
**Trade-offs**: More initial setup time, but better long-term development experience
**References**: CLAUDE.md, .claude/skills/

## [2026-02-12] Linting Tools Selection

**Decision**: ruff for Python backend, ESLint + Prettier for React frontend
**Context**: No linting or formatting tools were configured
**Choice**: ruff (Python), ESLint + Prettier (JS/React)
**Reasoning**: ruff is fast and combines linting + formatting for Python; ESLint + Prettier is the React standard
