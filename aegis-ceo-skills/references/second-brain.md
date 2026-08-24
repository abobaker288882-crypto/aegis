# Local second brain

Use the shared Obsidian vault at `~/Documents/Second Brain` when it exists. It serves every project, not only Aegis missions. It is ordinary local Markdown; Obsidian is the human interface, not a required integration layer.

## Retrieve with minimum context

1. Read `System/Current Context.md` once at mission boot.
2. Search `10 Projects/Project Graph.md` and its linked project nodes to locate every relevant real source path, including related project copies.
3. Extract a few distinctive terms from the mission and search those source paths directly with `rg -l` or `rg -n`.
4. Open only the smallest matching source files, project notes, or linked decision sections. Do not enumerate and read every note or repository file.
5. Prefer current repository, test, deployment, and live-system evidence when notes disagree or may be stale.
6. If no relevant note exists, continue without manufacturing background.

The project graph is a routing index and does not restrict access to the actual source. When projects have been added, moved, or removed, refresh it with the installed `second-brain-context/scripts/build_project_graph.py` before routing work.

Do not add an embedding service or knowledge-graph backend unless the user asks for one and its measured retrieval benefit justifies its setup, cost, and background work.

## Checkpoint only durable context

At a material checkpoint or final delivery, update the active project note with the outcome, acceptance criteria, current state, important decisions, blockers or risks, artifact paths, and next action. Update `System/Current Context.md` only when the active focus changes. Append to `System/Decisions.md` only when a decision would otherwise be rediscovered.

Keep checkpoints compact and merge with existing facts instead of appending a transcript. Never store prompts, chat transcripts, verbose command output, copied repository content, passwords, API keys, session tokens, private keys, or other secrets.
