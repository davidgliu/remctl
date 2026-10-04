# RemCTL 2.3.1 release validation

Verified on October 4, 2026. This is a local release candidate; it has not been published or tagged on GitHub. Issue [#60](https://github.com/viticci/remctl/issues/60) remains open pending publication.

## Shared fix

The common `cmd_edit` path previously carried a due-time alarm to midnight for a date-only target. It now clears that alarm instead. The condition remains narrow: every alarm must be absolute and match the old due time. It does not use the broader display-date match from the existing due-date clearing helper. Explicit alarm edits still take precedence.

All adapters call this implementation: the CLI and its aliases, typed MCP `update_reminder`, the Codex workspace, Claude Code, Claude Desktop, and Tailscale MCP. No adapter-specific alarm implementation was added.

## Regression and package checks

- Three focused regression tests cover one or duplicate matching alarms, custom alarms that match the display date, mixed absolute/relative/location configurations, and explicit absolute/relative overrides. The matching-alarm regression failed against the old code before the fix. Existing timed rescheduling and due-date clearing checks still pass.
- Protected Python 3.13 ran 885 tests in 284.195 seconds: 879 passed and six optional distribution checks skipped. Existing SQLite resource warnings remain.
- The four applicable prebuilt release checks passed separately: install/upgrade/rollback/uninstall, tamper rejection, runtime administrator authorization, and explicit signing migration.
- Python 3.14 passed 157 MCP and desktop-plugin tests. UI build, type checks, interaction contracts, and OpenAI extension schema checks passed. Claude Code strict plugin validation passed without warnings; its native Today mod runner passed five tests.
- Version fields in the CLI, both app fields, UI package/lockfile, and both plugin manifests are 2.3.1. Plugin launchers share build identifier `e3687400c8af5cd4`.
- All 34 release comparisons passed, including shared client modules, generated interfaces, packaged plugins/marketplace, signatures, app versions, and exact sealed Python code. All 41 installed comparisons passed, including both refreshed plugin caches.

## Installed and native acceptance

The official source installer preserved this Mac's Developer ID identity and existing protected Python. Doctor passed 16 checks with zero warnings/failures; the signed host reports Reminders, Automation, and Full Disk Access authorized. `remctl`, `rctl`, and `reminders` report 2.3.1 in a clean shell.

Before upgrading, a disposable reminder due October 15 at 16:00 with a matching absolute alarm reproduced the bug through installed 2.3.0 MCP. Its all-day edit left an alarm at midnight, and Computer verification in native Reminders showed Time on at 12:00 AM.

After upgrading:

| Path or case | Observed result |
| --- | --- |
| Installed CLI `edit -d 2026-10-15 --private` | Date-only due date, `allDay: true`, no alarm |
| Local typed MCP `update_reminder` | Date-only due date, no matching alarm |
| Codex and Claude Code cached plugin launchers | Matching due-time alarm cleared; fresh servers report 2.3.1 |
| Claude Desktop configured MCP launcher | Matching due-time alarm cleared; server reports 2.3.1 |
| Authenticated Tailscale MCP | Matching due-time alarm cleared; unauthenticated requests return 401 |
| Custom absolute alarm at 15:00 | Preserved when changing the due date to all-day |
| Explicit replacement alarm at 18:00 | Preserved with a date-only due date |
| Timed reschedule to 17:00 | Due date and its matching alarm both move to 17:00 |
| Installed Codex workspace, Remove due time then Save changes | All-day result read back with no alarm; inspector shows Add time |
| Native Reminders through Computer | Converted reminders show a date without a time; matching reminder's Time switch is off. Custom/explicit reminders retain 15:00/18:00 labels |

Fresh standalone and plugin MCP passed both legacy and modern protocol metadata checks (21 and 69 tools). Ordinary plugin responses remain data-only; explicit workspace and standalone widget resources load.

All six owned test reminders and their empty verification list were removed through local MCP and verified absent. No existing reminders were edited. A physical iPhone was not tested. Claude Code's model conversation was not rerun; plugin transport and its native mod tests were verified directly.

## Signed and notarized artifact

Both Developer ID apps and the final disk image were accepted by Apple, stapled, and validated. A quarantined copy of the finished image passed Gatekeeper; both apps mounted from it passed strict signatures and Gatekeeper as Notarized Developer ID software.

| Artifact | Verification value |
| --- | --- |
| App submission | `d8a5917a-f66a-4cd5-b3a3-d406d943f4b1` — Accepted |
| Disk image submission | `3e6f7279-c216-4f49-b1b4-2daa17cd2a5b` — Accepted |
| `RemCTL-arm64.dmg` SHA-256 | `acff84893036ddf5e1d9a0c67bd227dcbeb4c413366623c21036a22c54029ee3` |
| Bundled Python | `3.13.15` |
| Bundled protected runtime ID | `3b102ae2562c5bf4ef1b45e224d715e53541cab43931bc3de5548f36676904fd` |

Build and notarization receipts are under `.build/release-2.3.1`. Publication assets and notes are under `dist/2.3.1`. Acceptance scripts and results are `/tmp/remctl-231-*`; test/install logs and package audits are `/tmp/remctl-2.3.1-*`. The release does not require a new permission grant when upgrading the existing signing route. Installing its bundled protected runtime requires the normal administrator authorization; this Mac retained its already installed runtime.
