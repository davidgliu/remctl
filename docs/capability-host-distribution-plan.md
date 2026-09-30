# Capability Host installation and distribution

Original investigation: September 30, 2026. The sections below record the pre-implementation findings. Implementation now lives on the local `codex/remctl-distribution` branch; see [installation](installation.md) and [distribution validation](distribution-validation.md) for current behavior and evidence. End-to-end notarization and permission persistence remain release gates.

Board card: https://www.notion.so/3eb35e3fe8d88134983ec3d4a2c4bc16

## Recommendation

Offer a prebuilt, Developer ID-signed and notarized app as the ordinary installation path. Keep a free source-build path for contributors. Investigate a persistent, locally generated signing certificate for that path before requiring users to create an Apple account in Xcode.

The desired experience is one terminal command that installs the CLI and host and opens onboarding. Users still approve macOS privacy permissions. Do not promise an unattended permission grant.

The commands below describe a proposed interface; these options do not exist yet:

```sh
./install.sh --prebuilt
./install.sh --from-source
```

## Verified current behavior

- `install.sh` automatically selects an Apple Development identity, or accepts `REMCTL_CODESIGN_IDENTITY`. Live installation rejects ad-hoc signing and requires a Team ID and designated requirement: the rule macOS uses to recognize subsequent builds as the same app. Updates must preserve both.
- The host verifies its signature, nested code, and running executable against the bundle on disk. Its Python application archive is embedded in the executable. These checks must remain.
- The installer writes absolute Python, socket, and background-service paths into signed bundle resources. A prebuilt app cannot have these resources rewritten at installation without breaking its signature.
- The host runs an external Python 3.13+ interpreter. Its executable and ancestors must be root-owned and protected from ordinary user writes and extended access-control lists. Putting Python in the user-owned app and deleting this check would weaken the current execution boundary.
- The Python archive contains compiled bytecode. Release builds must pair it with the matching Python version.
- The inspected live app is arm64, signed with Apple Development, and has no hardened-runtime flag. The default keychains expose one valid Apple Development identity and no Developer ID Application identity. This does not establish whether a distribution certificate exists elsewhere.
- The plugin worktree launches the CLI through `python3` and `~/bin/remctl`. Removing the host's external Python dependency alone would therefore not remove Python from the overall installation.

Sources in this checkout: `install.sh`, `remctl-capability-host.swift`, `remctl_broker.py`, and `scripts/build_capability_archive.py`. Main checkout at inspection: `6409c09`. The plugin worktree has additional uncommitted work and is the integration baseline for its UI and packaging additions.

## Free source builds

### First candidate: a persistent local signing certificate

Apple documents that a self-signed certificate can establish a designated requirement and recognize subsequent versions of locally signed software. This is different from ad-hoc signing, which has no persistent certificate. Apple confirms that ad-hoc rebuilds can lose privacy permission identity.

A source installer could create a dedicated local signing key once and reuse it on updates. It would not need a paid developer membership or Apple account. This is a candidate design, not a verified RemCTL installation method.

Required work:

1. Prototype certificate creation and signing in an isolated keychain, without changing the default keychain search list or system trust settings. Determine whether normal local code validation works without broad trust overrides or interactive prompts.
2. Replace the unconditional Team ID requirement only for an explicit local-build mode. Require the expected bundle identifier and pinned signing certificate in the designated requirement. Keep strict signature verification and update continuity; do not use an identifier-only requirement.
3. Preserve the local key across updates. Report a missing or changed identity explicitly instead of silently creating a replacement and claiming permissions will carry over. Document that this identity is local to the user's Mac and is not a distribution credential.
4. Verify Full Disk Access, Reminders, and Automation on a disposable account or test Mac. Build version A, grant access, rebuild changed version B using the same key, restart, and verify all three grants and actual CLI behavior. A matching signature rule alone does not prove permission persistence.
5. Verify that a different key, a changed helper, and a tampered runtime are rejected. Verify failed installation restores the old service.

If this fails the permission test, retain Apple Development signing as the fallback. A free Xcode Personal Team is the next route to validate. Account authentication and first-time certificate setup are not established as a supported unattended terminal flow; do not promise they are.

Plain ad-hoc signing can be useful for isolated tests but is a poor default if normal rebuilds require users to repair permissions. Do not remove the existing gate and label that a completed fix.

## Prebuilt, notarized distribution

We obtain a Developer ID Application certificate and submit the finished release to Apple's notarization service. Users do not need their own Apple developer account, signing certificate, compiler, or paid membership. Notarization is Apple's automated malware/signature check, not App Store review; acceptance and private ReminderKit behavior still require actual validation.

Required work:

1. Separate building the immutable app from installing it. Derive user-specific socket and service paths at runtime from a constrained installation contract. Retain custom-prefix support deliberately, without admitting arbitrary executable paths or modifying signed resources.
2. Bundle a pinned Python runtime and required standard-library/native dependencies. Choose a layout that preserves protection against replacing the interpreter, imports, or helpers after validation. Compare a protected installation with a signed embedded runtime; do not waive the current root-ownership checks without replacing their guarantees. Include runtime license notices and an update policy.
3. Provide CLI and plugin launchers that use the bundled runtime. Preserve stdio MCP output, custom prefixes, and the existing rollback behavior. Ship the host, CLI modules, workspace HTML, and plugin fingerprint as one compatible release.
4. Sign nested executable code explicitly from the inside out with Developer ID, secure timestamps, and hardened runtime. Review only entitlements demonstrated necessary for EventKit, Apple Events, Python native modules, and the private helper. Do not add broad runtime exemptions preemptively or use `codesign --deep` as the release signing strategy.
5. Package the app, submit with `notarytool`, inspect its result/log, attach the notarization ticket using `stapler`, and validate the final archive. Submission and public release remain later actions; neither occurred in this investigation.
6. Test a quarantined download on a clean Mac without Xcode or externally installed Python. Verify install, permission onboarding, read and write behavior, plugin startup, update, rollback, and uninstall. Test the oldest supported macOS and current releases; verify each architecture advertised in release assets. The current arm64 installation is not proof of Intel support.

The current development-signed installation cannot silently become a Developer ID release while satisfying its exact designated-requirement continuity check. Treat switching signing modes as an explicit migration, retain rollback, and plan for permission onboarding again. Updates within either mode should preserve its established identity.

## Shared icon and thread coordination

Coordinating thread: **Plan RemCTL MCP Codex Plugin**, `01a0ef4b-75da-7e52-98fd-9b3e86e53890`.

Its worktree is `/Users/viticci/.codex/worktrees/remctl-desktop-plugin/remctl`:

- Artwork master: `plugins/remctl/assets/icon.png`.
- Native app icon: `assets/remctl.icns`.
- Provenance: `docs/icon-provenance.md`.
- `remctl-capability-host-Info.plist` already sets `CFBundleIconFile` to `remctl.icns`, and that worktree's installer copies it into the host's resources before signing.

The selected artwork has four translucent colored reminder circles, with a white check in the red circle. Reuse these files and existing integration. Do not replace or independently regenerate the icon. Integrate with the plugin worktree's additional archive modules, launcher, compiled UI, and release fingerprint rather than shipping main's older module list beside the new plugin.

## Next implementation sequence

1. Run the isolated local-certificate experiment and the permission-persistence check before selecting a default free-build signing mode.
2. Refactor build/install separation and runtime/path packaging around the coordinated plugin baseline.
3. Validate a local release candidate under hardened runtime, then obtain/select Developer ID credentials and submit for notarization when authorized.
4. Prove the downloadable release on a clean Mac, document the source-build path, and publish only after release approval.

## Apple references

- [Code Signing Tasks: local certificates and update identity](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html)
- [Understanding the Code Signature: designated requirements](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/AboutCS/AboutCS.html)
- [Apple DTS confirms ad-hoc rebuilds change privacy identity](https://developer.apple.com/forums/thread/819406)
- [Xcode signing workflow and Personal Teams](https://help.apple.com/xcode/mac/current/en.lproj/dev60b6fbbc7.html)
- [Notarizing macOS software before distribution](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- [Customizing the notarization workflow](https://developer.apple.com/documentation/security/customizing-the-notarization-workflow)
