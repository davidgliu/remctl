# RemCTL 2.3.0 release candidate

Prepared and installed on October 3, 2026, on the local `fix/issues-57-59` branch. Publication, tags, a remote push, and issue closure await Federico's approval. The candidate includes fixes for [#57](https://github.com/viticci/remctl/issues/57), [#58](https://github.com/viticci/remctl/issues/58), and [#59](https://github.com/viticci/remctl/issues/59); [their validation record](issues-57-59-2026-10-03.md) explains the implementation and actual Codex acceptance.

## Source and package checks

- The CLI, app version fields, UI package and lockfile, and both plugin manifests report 2.3.0. Both plugin launchers use build identifier `097ae8ad9288370a`, calculated from every shared Python module and both generated interfaces.
- The full Python 3.13 suite ran 882 tests in 312.670 seconds: 876 passed, six optional distribution tests skipped. The applicable release-bundle checks were then enabled separately: all four passed, covering install, upgrade, injected rollback, uninstall, tamper rejection, runtime administrator authorization, and signing migration. Existing SQLite resource warnings remain.
- Python 3.14 passed 122 focused MCP, desktop-plugin, and launcher tests. The UI build, type checks, interaction contracts, and official OpenAI extension schema checks passed.
- Claude Code strict plugin validation passed without warnings. Its native mod test runner passed all five Today-panel tests.
- All 34 release-package comparisons passed: client code, both generated interfaces, installer scripts, packaged plugins and marketplace, app version fields, signatures, and the exact sealed Python archive. The packaged CLI's interpreter wrapper was accounted for explicitly.
- Both Developer ID apps and the disk image were accepted by Apple, stapled, and validated. A quarantined copy of the finished image passed Gatekeeper; both mounted apps passed strict signature verification and Gatekeeper as Notarized Developer ID software.

| Artifact | Verification value |
| --- | --- |
| App notarization submission | `93e22e0d-8e94-471b-b093-efa44e62ac7e` — Accepted |
| Disk image notarization submission | `f86efbf4-5639-4a37-9878-8ac2b5da94a6` — Accepted |
| `RemCTL-arm64.dmg` SHA-256 | `9ee442a25239b7e563c6522c886b68d54d054740940e8b4064716f68acaabb83` |
| Bundled Python version | `3.13.15` |
| Bundled protected runtime ID | `141548bd912c49dac5be745a791fdc92d907d3ae869eff7ae159affe54b629c4` |

The release build and notarization receipts are under `.build/release-2.3.0`. Upload-ready copies of the disk image, checksum, and release notes are under `dist/2.3.0`.

## Installed acceptance

This Mac was reinstalled through the official source installer using its existing Developer ID identity and protected Python runtime. The packaged release's new runtime was tested in isolated installation prefixes; installing that runtime under `/Library/RemCTL/Python` requires an administrator password. This is a verified source-built 2.3.0 installation, rather than a claim that the new disk image's runtime replaced the existing one.

- In a clean shell, `remctl`, `rctl`, and `reminders` report 2.3.0 and return identical live list data.
- Doctor reports 16 checks, zero warnings, zero failures, and ready access through the signed Capability Host. Automation, Reminders, and Full Disk Access remain authorized. The installed app's strict signature verifies and its CDHash is `125cb0b7b65c420b4eadfc1f6c858bb7761475bc`.
- The repeatable installed-surface audit passes all 41 comparisons with no missing caches: 12 client modules, generated interfaces, packaged plugins, Codex and Claude Code caches, the exact embedded Python archive, and strict signature verification.
- Codex and Claude Code's normal plugin updaters installed 2.3.0. Both cached launchers initialize and execute real list and Smart List reads. Codex exposes 69 tools, including the two sidebar preference tools; Claude Code exposes the 21 standard tools. The configured Claude Desktop launcher also initializes at 2.3.0 and executes the same reads.
- Fresh installed standalone and plugin MCP sessions pass legacy and modern protocol paths, list reads, invalid-ID errors, explicit workspace resources, and standalone widget resources. Ordinary plugin tools return data without opening workspace tabs.
- The existing private Tailscale endpoint reports 2.3.0, exposes 21 tools, executes authenticated reads, and rejects an unauthenticated request with HTTP 401. Its token and access settings were retained.
- Computer reconnected RemCTL in Codex and verified live mixed-folder placement, collapse, Smart List navigation, movement of Smart Lists past ordinary lists, disabled boundary controls, folder movement at the top level, saved order through reinstall/reconnection, and scope-specific reset. Earlier live checks covered ordinary-list and pinned-tile ordering.
- The approved temporary workflow created only an empty folder, one empty list, and two Smart Lists that filtered that list. Exact object identifiers and zero reminder counts were checked before cleanup. CLI/MCP reads and Codex confirm every test item is absent; saved sidebar orders are restored to `{}`. No reminders were created or changed.

## Coverage limits

Testing ran on Apple silicon with macOS 27. Intel, older macOS releases, the reporter's account, and physical iPhone/iPad clients were not tested.

A fresh Claude Code agent conversation was attempted but could not execute its MCP call because the account had reached its weekly usage limit. This is unavailable acceptance, not a passing agent conversation. The real cached plugin launcher, configured MCP transport, strict manifest validation, and all five native Today-panel tests passed. Existing Claude Code conversations need a restart to apply the plugin update.
