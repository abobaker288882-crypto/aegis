# Aegis CEO Office

Read this reference when the active client supports an interactive visualization.

## Purpose

Open one top-down game-style Control Room when the mission begins. It should feel like a small management game, with rooms, worker characters, visible assignment handoffs, and movement between meetings, desks, the CEO office, verification, and launch. The visual is the user's window into Aegis; it must reflect real orchestration state rather than decorative or invented activity.

Opening the office is the mission's first user-visible action. Use only the canonical shell at `../assets/ceo-office-game.html`, copied with `../scripts/prepare-office.sh`; never replace it with a dashboard or card grid. Run movement, speech, and ambient effects locally in the client. Do not spend model turns generating animation frames or repeatedly rebuilding identical markup. The CEO may begin real mission work as soon as the office is visible; never wait for a decorative sequence to finish.

Show:

- the Sol CEO as a character in a dedicated office and at the meeting table during assignment or review;
- one visible desk or room per active worker, labeled with its actual model or system;
- each worker's bounded assignment, state, latest meaningful result, and relative or actual usage;
- a meeting room where characters gather while the CEO frames the mission and dispatches work;
- a CEO review surface where returned work is approved, revised, integrated, or rejected;
- a compact decision feed, mission progress, blocker state, and deployment state.

## State sequence

Animate only meaningful transitions:

1. CEO frames the mission and acceptance criteria.
2. Worker characters walk into the meeting and receive assignments through short dialogue bubbles.
3. Workers walk to their rooms and begin work, with restrained progress and state effects.
4. A worker carries a visible submission back to the CEO office.
5. The CEO approves it, requests a targeted revision, or reassigns it.
6. Approved work enters integration, verification, deployment, and live-check states.
7. The mission closes only after acceptance evidence passes.

Honor reduced-motion preferences. Animation must never imply that work occurred before evidence arrives.

Populate the roster from callable workers discovered in the current mission. Show Gemini/Antigravity and ChatGPT as separate characters so their assignments and results remain auditable. A named worker that is not callable may appear only as `Unavailable`; it must not walk into the meeting, receive an assignment, show progress, or return a result. Show either external worker as active only after a real task has been dispatched to that service.

Use a readable management-game aesthetic rather than a conventional analytics dashboard: a dominant office map, stable rooms, small character sprites, mission dialogue, and a compact HUD. Keep operational data accurate and subordinate to the office scene.

## Interaction

- Selecting a worker shows the complete current assignment and latest result.
- Approve continues the mission with that result.
- More work asks the CEO to identify one material gap and issue one efficient revision pass.
- Pause stops new assignments while preserving current work and state.
- Consequential approval displays the exact money or high-risk decision required.

Use host follow-up actions when available so controls steer the main Aegis task. Keep presentation-only selections local.

## Updating

Update the office at mission start and at meaningful state transitions. Preserve stable room positions and model identities so movement is easy to follow. Do not rebuild or narrate the panel for every command. If actual token or weekly-usage data is unavailable, show a clearly labeled relative estimate such as low, medium, or high.

Treat the office as one low-overhead status surface: client-side animation itself requires no model response, while creating the surface, interpreting new evidence, or publishing a state update may consume model/tool usage. Batch updates at meaningful milestones and reuse the same surface to minimize overhead.

If the visualization surface is unavailable, keep the same state model in a terse text Control Room. Never delay the mission merely to render the office.
