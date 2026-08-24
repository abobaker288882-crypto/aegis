---
name: second-brain-context
description: Retrieve and checkpoint compact project context in the user's shared local Obsidian Markdown vault. Use when starting, resuming, investigating, or finishing project work that may benefit from durable cross-session context; do not use for unrelated general questions.
---

# Shared project second brain

Use `~/Documents/Second Brain` as the durable context source for every project when that vault exists. Obsidian is the human interface; ordinary local Markdown access is the integration.

## Retrieve

1. Read `System/Current Context.md` once when cross-session context may matter.
2. Search filenames and content with `rg -l` or `rg -n` using a few distinctive terms from the request and current repository.
3. Open only the smallest matching project notes or linked decision sections. Never load the whole vault into model context.
4. Treat notes as leads and prefer current repository, tests, deployments, and live-system evidence when they disagree or may be stale.
5. Continue without invented background when no relevant note exists.

## Checkpoint

At a material checkpoint or final delivery, update the active project note with only the outcome, acceptance criteria, current state, important decisions, blockers or risks, artifact paths, and next action. Update `System/Current Context.md` only when active focus changes. Add to `System/Decisions.md` only when a decision would otherwise be rediscovered.

Merge with existing facts instead of appending transcripts. Never store prompts, chat transcripts, verbose tool output, copied repository content, passwords, API keys, session tokens, private keys, or other secrets.

Do not add embeddings, a knowledge graph, cloud sync, or background AI services unless the user asks and their measured benefit justifies setup, cost, privacy exposure, and ongoing work.
