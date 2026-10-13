# Selected Matt skills with an existing engineering workflow

This integration contract takes precedence over the upstream procedure below it.

- Read the project's AGENTS.md and, when present, `.claude/references/matt-integration.md` for routing and document locations. User instructions and existing authorization take precedence over skill defaults.
- When instructions say to call the Skill tool, invoke one named skill per call if the host provides that tool. Otherwise read that skill's installed SKILL.md and follow it. Do not assume a tool named Skill exists in every host.
- Reuse existing requirements, answers, specs, and approvals. Ask only material unresolved questions. A completed interview is input to a spec, not permission to implement or to bypass a spec review.
- Matt owns clarification, active domain modeling, and advisory architecture exploration. Addy owns specs, plans, implementation, testing, code review, and shipping. Handoff includes resolved requirements, constraints, decisions and their approval status, source paths, acceptance criteria, and open questions. Do not run a second interview over the same decisions.
- Follow existing glossary locations and ADR templates. Read architecture records and the identifier catalogue before proposing domain changes. Create a glossary lazily for agreed terms only, and write new ADRs as Proposed unless owner acceptance is recorded. Do not turn assumptions into accepted decisions.
- Keep the project's names for components, services, APIs, and boundaries. Matt's module/interface/seam vocabulary is an additional analytical lens, not a rename instruction. Frozen C3 records change only through the project's C3 change process, never direct edits.
- Architecture exploration produces evidence and proposals, not an automatic refactor. Use Archify when the user wants an architecture map or its interactive visualization fits the assessment; retain before/after evidence when comparing candidates. Existing diagrams and ADRs remain authoritative.
- Preserve the project's testing doctrine and existing tests. Do not replace real integration/contract tests with mocks or delete tests merely because a module was deepened. Addy governs implementation and verification after the approach is approved.
- Delegate only when the host and project permit it. Sequential exploration is a valid fallback; ordinary clarification does not require a multi-agent fan-out.
- These five skills need no ticket tracker, full Matt setup, plugin installation, or global symlinks. Never require an uninstalled Matt skill to finish this workflow.
