# Local second brain

Use the shared Obsidian vault at `~/Documents/Second Brain` when it exists. It serves every project, not only Aegis missions. It is ordinary local Markdown; Obsidian is the human interface, not a required integration layer.

## Retrieve with minimum context

1. Read `System/Current Context.md` once at mission boot.
2. Extract a few distinctive terms from the mission and search the vault with `rg -l` or `rg -n`.
3. Open only the smallest matching project notes or linked decision sections. Do not enumerate and read every note.
4. Prefer current repository, test, deployment, and live-system evidence when notes disagree or may be stale.
5. If no relevant note exists, continue without manufacturing background.

Do not add an embedding service or knowledge-graph backend unless the user asks for one and its measured retrieval benefit justifies its setup, cost, and background work.

## Checkpoint only durable context

At a material checkpoint or final delivery, update the active project note with the outcome, acceptance criteria, current state, important decisions, blockers or risks, artifact paths, and next action. Update `System/Current Context.md` only when the active focus changes. Append to `System/Decisions.md` only when a decision would otherwise be rediscovered.

Keep checkpoints compact and merge with existing facts instead of appending a transcript. Never store prompts, chat transcripts, verbose command output, copied repository content, passwords, API keys, session tokens, private keys, or other secrets.
