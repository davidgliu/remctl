---
name: onboarding
description: Set up the standalone RemCTL desktop plugin and its local Apple Reminders access.
---
Use the standalone RemCTL MCP server. Never route this plugin through Mac Remote or any remote adapter.

1. Call `doctor` and inspect `access.effective`. The signed RemCTL Capability Host owns the macOS permissions. Never tell users to grant access to Python, Terminal, or Codex.
2. If the host is missing, explain that the RemCTL CLI and signed host must be installed using the repository's installer. If access is blocked, show the specific missing permission and the RemCTL onboarding command. Do not claim setup succeeded until doctor reports ready.
3. Read `read_settings` and `lists`. Ask which existing list should be the default for new reminders, and offer the advanced Reminders features with their private ReminderKit caveat. Use `update_settings` only for choices the user makes. Ordinary workspace reads do not require opting in.
4. Call `open_workspace`. Explain in one sentence that selecting reminders and choosing Attach supplies only those reminders to the conversation. The workspace is desktop-only.

A duplicate standalone MCP connection may exist from an older CLI install. Keep one effective RemCTL connection in Codex and preserve the other clients' configuration.
