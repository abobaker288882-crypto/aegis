---
name: usage-optimizer
description: Reduce Codex token and weekly usage for multi-step implementation, investigation, research, or artifact work while preserving the user's requested quality and verification bar. Use when the user asks to conserve quota, reduce tokens, make execution more efficient, or find a lower-usage way to complete substantial work; do not invoke for a trivial answer where the optimization overhead would cost more than it saves.
---

# Usage Optimizer

Minimize usage subject to completing the user's actual request correctly. Do the work unless the user asks only for an optimization plan.

## Set the floor

Before costly work, capture a tiny internal contract:

- outcome and scope;
- non-negotiable quality, source, tool, or format requirements;
- evidence that will prove completion;
- risk, privacy, and external-side-effect constraints.

Never lower this floor to save usage. Preserve user-requested depth, mandatory checks, current-source verification, safety review, and approval boundaries.

## Choose the lean route

Classify the task using observable evidence, not invented token counts:

- **Bounded:** the target and method are clear. Work directly with the narrowest useful inspection and check.
- **Exploratory:** the location or cause is unknown. Search indexes and failure evidence first, then narrow quickly.
- **Expansive:** the request is broad, ambiguous, repository-wide, or research-heavy. Define acceptance evidence, partition only independent work that benefits from it, and keep the shared context compact.

Use these levers in order:

1. Reuse user-provided context, existing artifacts, prior results, repository conventions, and cached evidence.
2. Prefer deterministic inspection, indexed search, scripts, compilers, and tests over speculative reasoning.
3. Batch independent read-only operations. Read relevant ranges and files instead of dumping whole trees or documents.
4. Change the smallest coherent surface that satisfies the request.
5. Run the narrowest check that directly proves the behavior. Widen checks only when risk, shared impact, or a failure justifies it.
6. Delegate only a bounded independent unit when the expected saved context or latency exceeds briefing and integration overhead. Route it to the least expensive capable worker and request an artifact or compact evidence, not an essay.
7. Keep one compact ledger of constraints, decisions, evidence, and open blockers. Reuse it instead of re-reading or re-deriving.

Before a costly action, ask internally: *What decision will this resolve, and could the result change the next action?* Skip it when neither answer is concrete.

## Protect quality and privacy

- Never claim actual tokens, remaining weekly quota, savings, or model cost unless a tool exposed those values. Otherwise label estimates as relative proxies.
- Useful proxies are files or sources opened, duplicated context, breadth of search, model/tool calls, test scope, retry count, and unresolved uncertainty.
- Do not send private source, secrets, credentials, personal data, or confidential material to an external service merely to save Codex usage.
- For high-stakes, security-sensitive, legal, medical, financial, destructive, or externally mutating work, spend the verification needed for the risk. Efficiency changes routing and context size, not the safety bar.
- Follow any required skill or user-specified workflow even when a cheaper route exists.

## Retry and stop

- Stop exploring when one supported path satisfies the contract and its direct evidence passes.
- After two materially identical failed attempts, do not repeat the approach. Inspect the failure and choose a different diagnostic or ask the minimum blocking question.
- Do not spend usage on optional polish, duplicated reviews, speculative edge cases, or extra deliverables outside the request.
- If different interpretations would materially change the product, ask one concise question rather than exploring every branch.
- Finish with the result, verification status, and only material residual uncertainty. Keep the handoff concise.

## Optional route helper

For a genuinely multi-step task whose route is unclear, run `scripts/route_task.py --help` and provide its compact JSON result as an internal routing hint. Skip the helper for obvious work; its result cannot override the user's requirements, safety rules, or direct repository evidence.
