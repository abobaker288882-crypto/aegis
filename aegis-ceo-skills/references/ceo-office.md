# Aegis CEO Mission Graph

Read this reference when the active client supports an interactive visualization.

## Purpose

Open one simple mission graph when Aegis begins. Use only the canonical fragment at `../assets/ceo-mission-graph.html`, copied with `../scripts/prepare-office.sh`. The graph is a reliable status surface, not a simulation: Sol CEO appears at the top, callable workers below, and the delivery pipeline ends in Integrate, Verify, and Ship.

Show each worker's actual model or system, state, one-line current assignment, latest meaningful result, and exposed usage or a clearly labeled relative estimate. Antigravity, Gemini, and ChatGPT remain separate nodes so their real assignments are auditable. A worker may show `Active`, `Assigned`, or `Working` only after the corresponding service actually responded or received work. Otherwise show `Connecting`, `Blocked`, or `Unavailable`.

## Updating

Open the copied graph once at mission start. Keep node positions stable. Selecting a node must reveal its full bounded assignment and latest result. The graph's `window.AegisMissionGraph.setState(...)` method can update phase, usage, workers, pipeline, and the decision feed when the host can call it without another model turn. Otherwise leave the graph unchanged during ordinary work and reopen it only for a material blocker or the final verified state.

Do not animate, simulate progress, invent usage, or replay a fake mission. Do not spend model turns redrawing the graph. Batch state updates and continue substantive work immediately after the graph is visible.

If the visualization surface is unavailable, use the same state in a terse text Control Room. Never delay the mission to render status.
