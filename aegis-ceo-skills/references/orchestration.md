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

## Usage governor

Apply before every model assignment and repair loop. Minimize Codex usage without weakening acceptance evidence.

### Default profile: dual-objective efficiency

The two objectives are production-ready quality and the least possible Codex weekly usage. Optimize them together: preserve every required acceptance check while refusing calls that do not add material evidence or user value. Use this profile unless the user explicitly changes the tradeoff:

1. One batched deterministic discovery pass produces the mission contract and acceptance checks.
2. One compact Antigravity assignment owns the largest coherent implementation workstream, inspects the repository itself, edits in scope, runs relevant checks, and returns only changed paths, check results, blockers, and the next material decision.
3. One independent Gemini assignment critiques the built artifact against acceptance checks and names only material defects. For complex products, authentication, authorization, payments, sensitive data, migrations, or production deployment, do not skip proportionate independent review merely to save usage.
4. Deterministic tools inspect the diff, build, test, lint, scan, and exercise the product. Do not ask another model to repeat passing evidence.
5. Send failed evidence back through the existing external conversation for a targeted repair. Repeat for every named remaining failure, material defect, or high-severity risk until the evidence passes; there is no fixed repair cap.
6. Sol performs necessary integration judgment and final acceptance. Add Luna, Terra, specialized review, or deeper Sol reasoning whenever earlier routes leave material uncertainty or a weaker product. Never declare completion to protect the usage target.

The mission graph opens once and remains static during normal work. Update it only for a blocker that requires user action or the final verified state. Do not spend a model turn merely to refresh status.

Before every Codex assignment, state internally which unmet acceptance check, unresolved risk, or integration decision the call will address. If no concrete item exists, skip it. If equivalent evidence can come from reuse, deterministic tools, or an authenticated external worker, use that route. Start with the cheapest capable Codex model and lowest reasoning effort; escalate only when observed evidence fails. Once all material acceptance checks pass, stop immediately.

### Route in this order

1. **Reuse:** existing result, session, artifact, decision, test output, or cached context.
2. **Deterministic:** batched inspection, search, scripts, structured queries, builds, and tests; reduce large outputs before CEO review.
3. **External:** one compact non-sensitive brief per worker and phase. Antigravity owns the largest coherent build; Gemini and ChatGPT get distinct research or critique.
4. **Luna/low:** bounded Codex-only work or an independent check whose expected quality benefit exceeds its coordination cost.
5. **Terra/low or medium:** integration, debugging, implementation, or review when earlier routes leave a material gap or uncertainty.
6. **Sol:** mission framing and acceptance; extra reasoning only for architecture, ambiguity, hard failures, security-sensitive judgment, or synthesis. Use high, xhigh, max, pro, or equivalent only for a named unresolved criterion with plausible measured benefit.

Skip a delegation when its briefing, coordination, and synthesis cost is likely to equal or exceed doing the bounded work directly. Never create a worker merely to restate status, re-read evidence the CEO already has, or provide a ceremonial review.

### Compact context protocol

Keep stable instructions short and ordered consistently. A worker receives only:

- bounded outcome and acceptance check;
- exact relevant paths, symbols, snippets, or failing evidence;
- constraints, privacy boundary, and non-goals;
- required artifact location or concise return schema.

Do not send transcripts, repository dumps, repeated policy, passed evidence, or outputs available by path. Put substantial work in an artifact; return only result, changed paths, checks, blockers, and next material decision.

### Turn and loop control

- Batch related questions. Parallelize only independent critical-path work worth its coordination cost.
- Default to one primary pass plus one targeted repair. Continue only for named failed evidence, unresolved high-severity risk, or a specific material gain.
- Reuse external conversations. Start fresh only for contamination, privacy, or task divergence.
- After localized repairs, prefer targeted tests unless dependency reach or release risk warrants a broad suite.
- Stop immediately when acceptance evidence passes. Do not spend tokens seeking stylistic consensus, repeated reassurance, or speculative polish.

If an actual usage or credit signal is exposed, record it at mission start and meaningful milestones. Never invent token counts or remaining weekly quota. When the signal is near its limit, enter conservation mode: no optional Codex delegation or duplicate review; use deterministic checks and available external workers, while Sol performs only indispensable integration and final acceptance.

## Required activation gate

Antigravity and Gemini must be active for every Aegis mission unless the user explicitly waives one for that mission. Before planning or implementation:

1. Discover native provider tools and reusable existing worker sessions.
2. If absent, discover a documented provider CLI or existing local command and use it through the integrated terminal. Do not guess command names or flags; inspect installed commands, built-in help, or authoritative provider documentation. A command that only launches an app is not a callable worker. For Antigravity, read and apply [antigravity-cli.md](antigravity-cli.md) when `agy` is available.
3. If there is no supported CLI, use an existing recorded Computer Use workflow for the installed desktop app. For Antigravity on macOS, read [antigravity-desktop.md](antigravity-desktop.md). Target stable app, window, and control labels rather than screen coordinates; keep prompts free of secrets. If no recording exists, request the smallest one-time setup: have the user demonstrate opening the app, starting or selecting a session, sending a harmless probe, and returning to the response.
4. If neither local route works, check for an already-authenticated controllable browser session.
5. Start or claim the service and send a minimal, non-sensitive capability probe.
6. Record `Active` only after a successful provider response; keep the mission graph at `Connecting` during real attempts.
7. Try one materially different supported access route after a failure.
8. If workflow recording, sign-in, credentials, installation, account creation, payment, or new permissions are required, stop at that boundary with the smallest exact request. Do not begin the mission with a substitute while claiming the required worker is active.

Do not repeatedly retry an unchanged blocked route. Once connected, keep both sessions alive and reuse them across the mission instead of reopening or reauthenticating them.

When the host exposes model selection, keep the primary Aegis CEO role on Sol. If that is unavailable, use the strongest available model and label the substitution in the Control Room; do not interrupt the mission merely to obtain the preferred label.

Use ChatGPT for research, comparison, summaries, and UX/content critique; Antigravity for the largest implementation and repair volume; and Gemini for synthesis, alternatives, drafts, and independent critique. These are preferences, not fictional dependencies. Substitute accurately when unavailable and never spend more Codex usage reaching a preferred worker than it can save.

Discover all three external services before composing the roster. An authenticated browser session counts only when it is actually controllable and the required task can be performed safely. If a service is unavailable, do not create its assignment, queue entry, active state, or result; mark it `Unavailable` and continue with real workers. Never use an Antigravity, Gemini, or ChatGPT label for work performed by Sol, Luna, Terra, another provider, or deterministic tools.

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
