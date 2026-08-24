# Antigravity CLI worker

Use the official Antigravity CLI before desktop Computer Use. Discover it with `command -v agy`; on macOS also check `~/.local/bin/agy`. Confirm the installed command with `agy --version` and discover current model identifiers with `agy models` rather than assuming availability.

## Activate

Send a minimal non-sensitive probe in structured print mode:

```sh
agy --model gemini-3.7-flash-low --effort low --sandbox --output-format json --print='Reply with exactly AEGIS_CLI_READY and nothing else.'
```

Attach the prompt directly to `--print=`; otherwise the CLI can consume the next flag as the prompt. Mark the worker `Active` only when the process exits successfully, the JSON status is `SUCCESS`, and the response matches the probe. Capture `conversation_id` for reuse.

## Assign and reuse

- Batch the largest coherent non-sensitive assignment into one compact prompt. A new CLI turn can carry substantial provider-side input context even for a short prompt.
- Default to the lowest available Gemini Flash model and low effort that can pass the acceptance check. Raise the model or effort only for a named failure or material quality risk.
- Use `--sandbox` by default. Add `--mode accept-edits` only when the bounded assignment explicitly requires workspace edits. Never use `--dangerously-skip-permissions` as an efficiency shortcut.
- Continue related work with `--conversation <conversation_id>` and another attached `--print=` prompt. Start a new conversation only for privacy, contamination, or unrelated work.
- Prefer `--output-format json`; retain only the response, status, conversation ID, and exposed usage summary. Treat that usage as Antigravity/provider usage, not as Codex weekly usage.
- Keep secrets and sensitive source out of prompts unless the mission's authorization explicitly permits transmission to the provider.

## Verified route

Antigravity CLI 1.1.19 was installed from Google's checksum-verifying installer at `~/.local/bin/agy`. The authenticated CLI listed Gemini models, Gemini 3.7 Flash Low returned the exact probe `AEGIS_CLI_READY`, JSON mode returned `status`, `response`, `conversation_id`, and usage fields, and `--conversation` successfully reused the same session. Availability, models, limits, and account terms may change; re-check the live command instead of treating this record as permanent.
