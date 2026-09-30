# Distribution implementation and validation

September 30, 2026. Local branch: `codex/remctl-distribution`. No push, main update or public release.

## Implemented paths

- `./install.sh`: download the native-architecture DMG, verify the MacStories Developer ID and Gatekeeper acceptance, then install the immutable app and matching CLI.
- `./install.sh --from-source`: fetch checksum-pinned Python, compile the host/helpers, create or reuse an owner-only local signing key, verify the resulting app, and run the same installer.
- `--prebuilt APP`: install a reviewed existing build. Local certificate builds require `--allow-local-build`; ad-hoc signatures fail.
- Runtime installation uses an administrator-authorized native host command. It copies only the manifest-verified Python tree into a root-owned content-addressed directory. It never edits an existing system Python.
- Staged update, rollback and uninstall retain the existing ownership-manifest checks. Switching signing identities requires explicit `--migrate-signing`.

## Current evidence

| Check | Result |
| --- | --- |
| Complete arm64 local app build | Passed, including Python 3.13.15 and shared icon |
| One-command source build and dry run | Passed |
| Strict nested code signature verification | Passed |
| Persistent local key, changed binary under same identity, other-key rejection | Passed |
| Keychain search list preservation and private-file checks | Passed |
| Pinned archive extraction, traversal and symlink rejection | Passed |
| Isolated prebuilt install, update, injected publication failure, rollback, uninstall | Passed |
| Tampered bundle rejection and non-admin runtime-install rejection | Passed |
| Existing installer suite | 24 tests passed |
| Capability transport/archive/planner/diagnostics | 99 tests passed |
| CLI/MCP/desktop/events | 563 tests passed |
| Native host original identity, post-start resign rejection, sealed invocation/broker | 4 tests passed |
| Distribution-focused tests | 8 tests passed, including explicit signing migration |

Simulation uses temporary prefixes and does not install a live LaunchAgent or grant permissions. These results do not prove fresh-machine permissions, protected-runtime installation or notarization.

## Remaining release gates

- Install the bundled runtime with administrator authorization and run the actual installed shell launcher and sealed broker.
- Grant permissions to a local certificate build, change/rebuild it with the same key, and verify the grants still work. Do not infer this from designated-requirement checks alone.
- Build using Developer ID, obtain Apple's notarization acceptance, staple the app and DMG, and validate Gatekeeper acceptance on the final artifact.
- Validate the Intel artifact and the advertised minimum macOS version on appropriate systems. Cross compilation alone is insufficient.
- Final local app matches the coordinated desktop UI: HTML SHA-256 `06e2d56c86bc7fa750579b5ebafdc799cf1e444f2de103cebd95900f37b0b50f`, imported from the desktop plugin thread and fingerprint recomputed for this branch. That thread independently verified the live UI. Packaged HTML, plugin fingerprint, icon and installer byte parity passed in this branch.

## Build a release locally

```bash
python3 scripts/build_distribution.py --release \
  --identity 'Developer ID Application: …' --output dist/release-arm64
scripts/notarize_distribution.sh dist/release-arm64 --asc
```

`--asc` uses the existing App Store Connect CLI credential. Alternatively pass a `notarytool` keychain profile as the second argument. The script submits the app, requires Accepted, staples and verifies it, creates a DMG with the installer, submits and staples that DMG, checks Gatekeeper, and writes a SHA-256 receipt. Rejected submissions retain result/log files. Notarization uploads to Apple; it does not publish a GitHub release.

Build on each supported architecture. Artifacts are `RemCTL-arm64.dmg` and `RemCTL-x86_64.dmg`. Do not publish an architecture before its runtime and permission checks pass.

## Signing credential check

The M5 and M3 Ultra active keychains expose the same Apple Development identity and no usable Developer ID identity. The M3 was checked through its saved Screen Sharing connection because SSH authentication was unavailable. Xcode on the M5 is signed in and offers Developer ID Application creation; the required final computer-use confirmation is pending. The existing MacStories App Store Connect credential validates and can read notarization history. No new Apple certificate or notarization submission has been made yet.
