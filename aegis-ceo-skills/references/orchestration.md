# Aegis Orchestration

Read this reference for any multi-model, multi-session, or end-to-end product mission.

## Mission contract

Turn the user's brief into an internal mission contract without returning a long plan:

- target outcome and intended user;
- observable acceptance criteria;
- repository, environment, and deployment target;
- material constraints, including cost and privacy;
- evidence required before completion.

Resolve routine ambiguity yourself. If the brief is incomplete, choose reversible defaults that preserve future options. Ask one short question only when different answers would create materially different products or cross an approval boundary.

## Routing hierarchy

The CEO retains mission state, architecture, risk decisions, and final acceptance. Delegate bounded work with minimal context and a concrete expected artifact.

When the host exposes model selection, keep the primary Aegis CEO role on Sol. If that is unavailable, use the strongest available model and label the substitution in the Control Room; do not interrupt the mission merely to obtain the preferred label.

Use the following external-first routing intent, adapted to what is actually available:

- ChatGPT chat: research, ideation, comparisons, summaries, content critique, and other work that can preserve Codex quota without exposing sensitive data.
- Antigravity/Gemini or another capable external worker: large self-contained implementation, research synthesis, visual/product exploration, or an independent critique when accessible and efficient.
- Luna: high-volume, low-risk, well-specified edits, searches, test additions, documentation, formatting, and mechanical tasks.
- Terra: normal implementation, debugging, integration, review, and tasks requiring balanced judgment.
- Sol: CEO role, architecture, ambiguous or high-risk reasoning, hard debugging, cross-workstream integration, security-sensitive decisions, and final acceptance.

These are preferences, not fictional dependencies. If a named worker is unavailable, select the closest available substitute and identify it accurately in the Control Room. Do not spend more Codex tokens attempting to reach a preferred worker than the task would save.

For a substantial end-to-end mission, callable Gemini/Antigravity and ChatGPT chat should perform most suitable reasoning volume. Give each multiple non-overlapping assignments across the mission—for example discovery, competing product approaches, implementation drafts, edge-case discovery, cross-review, and targeted repair—until acceptance evidence passes or another pass has low expected value. Use their different outputs to cross-check consequential decisions instead of asking both identical generic questions.

Discover both services before composing the roster. An authenticated browser session counts only when it is actually controllable and the required task can be performed safely. If either service is unavailable, do not create its assignment, queue entry, meeting participant, progress animation, or result; mark it `Unavailable` and continue with real workers. Never use a Gemini or ChatGPT label for work performed by Sol, Luna, Terra, another provider, or deterministic tools.

## External-worker loop

1. Send mission discovery and solution exploration to Gemini and ChatGPT in parallel with different perspectives.
2. Route large self-contained implementation or visual exploration to Gemini/Antigravity; route research, comparison, content, UX critique, and independent reasoning to ChatGPT.
3. Cross-review important outputs: give each external worker a compact artifact from the other when privacy permits, and request only concrete defects or improvements.
4. Return failed acceptance evidence as targeted repair briefs to the most suitable external worker before spending Sol on implementation detail.
5. Stop external passes when acceptance evidence is complete, rate limits intervene, or the next pass is unlikely to materially improve the product.

## Worker briefs

Each worker brief should contain only:

- one bounded outcome;
- the minimum relevant files or context;
- constraints and non-goals;
- required evidence or output format;
- where the result should be written or returned.

Prefer patches, file paths, commands with observed results, or compact findings over essays. Do not ask multiple workers to solve the same task unless independent comparison is likely to prevent a material error.

Parallelize independent critical-path work only when its expected time or quality gain exceeds coordination and usage cost. Keep dependent work sequential.

## CEO loop

1. Frame the mission and acceptance evidence.
2. Inspect existing state using direct tools.
3. Route only work that benefits from delegation.
4. Integrate outputs into one coherent product.
5. Run deterministic checks and inspect the real experience.
6. Perform a proportionate security and failure-state review.
7. Commit coherent in-scope changes without absorbing unrelated user changes.
8. Deploy through the available existing infrastructure.
9. Verify the live system and repair or roll back failures.
10. Repeat only for failed criteria or material defects, then return the finished result.

Do not loop on subjective polish after acceptance criteria pass. Before another loop, state internally what failed, what change is expected to fix it, and what evidence will prove the fix.

## Full-product verification

Derive checks from the product. For software, consider:

- frontend behavior, responsive states, accessibility, and important visual defects;
- API contracts, backend behavior, persistence, migrations, and concurrency where relevant;
- authentication, authorization, input validation, output encoding, secret handling, and dependency exposure;
- empty, loading, error, retry, and recovery states;
- integration behavior with real or representative services;
- build, lint, type, unit, integration, and end-to-end checks relevant to the stack;
- production configuration, health, logs, and critical live journeys.

Security depth must match exposure and impact. Do not claim a comprehensive security audit unless that audit was actually performed. For high-risk products, use an available specialized security workflow rather than a superficial checklist.

## Persistence and blockers

Continue safe in-scope work until acceptance criteria pass. A temporary failure is not a reason to return early: diagnose it, try a materially different approach, use a suitable worker, or advance another workstream.

Stop and ask only when completion requires missing authority, money, inaccessible credentials or systems, a product-defining user choice, or an exceptional risk. Report the exact blocker and the smallest decision or access needed. Never hide incomplete work behind a polished final summary.
