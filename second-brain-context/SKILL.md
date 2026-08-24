---
name: second-brain-context
description: Route across the user's full local project graph, retrieve compact source context, and checkpoint durable decisions in a shared Obsidian vault. Use when starting, resuming, investigating, or finishing project work; do not use for unrelated general questions.
---

# Shared project second brain

Use `~/Documents/Second Brain` as the durable context source for every project when that vault exists. Obsidian is the human interface; ordinary local Markdown access is the integration.

The graph is a routing index, not a copy of the projects. `10 Projects/Project Graph.md` links project nodes to their real source folders and technology nodes. When the graph is missing, stale, or explicitly requested, refresh it with this skill's `scripts/build_project_graph.py`. Add `--root <path>` for project roots outside the default Documents, Desktop, Downloads, Developer, Projects, and Code locations.

## Retrieve

1. Read `System/Current Context.md` once when cross-session context may matter.
2. Search `10 Projects/Project Graph.md` and its linked project nodes to locate the real source path.
3. Search that source directly with `rg -l` or `rg -n` using a few distinctive terms from the request. The graph never limits access to the actual project files.
4. Open only the smallest matching source files, project notes, or linked decision sections. Never load the whole vault or repository into model context.
5. Treat notes as leads and prefer current repository, tests, deployments, and live-system evidence when they disagree or may be stale.
6. Continue without invented background when no relevant note exists.

## Checkpoint

At a material checkpoint or final delivery, update the active project note with only the outcome, acceptance criteria, current state, important decisions, blockers or risks, artifact paths, and next action. Update `System/Current Context.md` only when active focus changes. Add to `System/Decisions.md` only when a decision would otherwise be rediscovered.

Merge with existing facts instead of appending transcripts. Never store prompts, chat transcripts, verbose tool output, copied repository content, passwords, API keys, session tokens, private keys, or other secrets.

Do not add embeddings, a knowledge graph, cloud sync, or background AI services unless the user asks and their measured benefit justifies setup, cost, privacy exposure, and ongoing work.

The local Obsidian wikilink graph is permitted and preferred. Never copy `.env` files, credentials, private keys, dependency trees, build output, caches, or whole repositories into the vault. The graph generator records paths, safe project metadata, and relationships only.
