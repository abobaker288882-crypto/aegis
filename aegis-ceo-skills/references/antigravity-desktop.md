# Antigravity desktop worker

Use this route only when `/Applications/Antigravity.app` is installed and no native Antigravity connector or supported CLI is available. Control it with Computer Use through the app name `Antigravity`; if name resolution fails, retry with bundle identifier `com.google.antigravity`.

## Connection boundary

Antigravity Desktop 2.9.1 exposes an `antigravity://` deep-link handler and loopback services, but its bundled app contains no supported command for submitting chat prompts. The deep link may open or focus the app; it is not proof of model access. Do not call undocumented localhost services or reverse-engineer their authorization. Use the verified Computer Use flow below until Antigravity exposes a documented connector or CLI, then prefer that supported route after a harmless response probe.

## Start or reuse

1. Read a fresh accessibility state. Prefer an existing conversation dedicated to the current Aegis mission; otherwise activate the stable `New Conversation` control.
2. Use the workspace project only when an exact relevant project is already available and the assignment requires repository context. For research, probes, or general tasks, choose `No Project`. Never select an unrelated project merely because one is open.
3. Confirm the visible model selector. The recorded working route exposed `Select model, current: Gemini 3.7 Flash Medium`; report the actual visible model and do not assume it remains unchanged.
4. Activate the `Message input`, enter the bounded worker brief, then activate `Send message`. Use accessibility element labels and refresh state after every action; element indexes are ephemeral.
5. While the response shows `Working` or the composer exposes `Cancel`, keep the worker in `Working`. Re-read state at bounded intervals. Treat the task as returned only when the working indicator is gone and a new `Agent response` contains substantive text.
6. Capture the returned text compactly and reuse the same conversation for related follow-ups. Start another conversation when context separation materially improves accuracy or privacy.

## Verified route

The recorded and replay-tested flow opened Antigravity, used `No Project`, sent a harmless prompt through the `Message input`, observed Gemini 3.7 Flash Medium, waited for `Working` to finish, and received the exact capability response `AEGIS_READY`. This proves UI reachability, not unlimited access, pricing, or suitability for sensitive data.

Never send credentials, secrets, private source, personal data, or confidential business material through this route without the authorization required by the main skill.
