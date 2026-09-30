# Desktop plugin packaging handoff

September 30, 2026. Integration baseline: the `remctl-desktop-plugin` worktree, installed as plugin 0.2.2. The separate distribution investigation is tracked on [the Coding Projects board](https://www.notion.so/3eb35e3fe8d88134983ec3d4a2c4bc16); its plan lives in the primary checkout at `docs/capability-host-distribution-plan.md`. This note records desktop integration requirements, not another distribution proposal.

## Selected icon

Use the four-circle translucent iMac G3 variant already installed for both the plugin and Capability Host. The master is `plugins/remctl/assets/icon.png` (1254 × 1254); the native export is `assets/remctl.icns`. MCP exports are `assets/remctl-mcp-icon-512.png` and `assets/remctl-mcp-icon.png`; permission artwork is `assets/remctl-permissions-icon.png`. The generation prompt is in [icon provenance](icon-provenance.md). No new export is needed.

## Runtime requirements

- The current installer writes absolute Python, socket and LaunchAgent paths into bundle resources before signing. A prebuilt bundle cannot simply be copied between users and rewritten afterward without invalidating its signature. Portable configuration needs an explicit design.
- The sealed Python archive is embedded in the native executable and checks the exact Python patch version, cache tag and bytecode magic. A distributable host needs a compatible protected runtime; installing an arbitrary Python 3.13 is insufficient.
- The plugin currently launches `~/bin/remctl` through `python3`. A self-contained download must cover the CLI and plugin launch path as well as the app's internal interpreter.
- Ship the MCP, Events, plugin and workspace Python modules, generated workspace HTML, native helpers, artwork and plugin manifest as a matching release. End users do not need Node to use the prebuilt HTML.
- Preserve the signed host trust checks and private Reminders permission identity. Persistent self-signed source builds need real permission persistence validation before becoming an advertised installation path. Ad-hoc signing is not an equivalent substitute.
- The current install generates native list badges on the user's Mac. Keep that local generation step in the packaging design.

Prefer a notarized, bundled-runtime download for ordinary users. Keep account-free source builds as a separately verified path. This Events retry changed no installer, signing identity, certificate, live runtime or launch service.

## Final UI refinement handoff — September 30

Events acceptance is deferred; everyday Activity/Watch UI entry points are hidden. Import the final `ui/src/main.tsx`, `ui/src/style.css`, new `ui/src/date-editor.tsx`, and `remctl_workspace.html` from the desktop-plugin worktree. The matching UI/runtime fingerprint is `53e02600ba62dc06`; preserve distribution's launcher changes when updating `plugins/remctl/mcp.json`, then regenerate the fingerprint if distribution changes any hashed runtime files. No installer, launcher, signing, artwork, or Python source was edited during this final UI refinement pass.

Acceptance and screenshots are in `desktop-plugin-validation.md`; the updated `desktop-try-it.md` contains ten practical desktop exercises. The local signed-host installation preserved its identity and passed diagnostics.
