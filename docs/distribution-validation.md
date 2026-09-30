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
| Default download with no published artifact | Reports HTTP 404 and exits with failure; no silent fallback |
| Notarization of a local certificate build | Rejected before submission |
| Packaged license notices | Project, Python and locked UI dependency notices included |
| Protected free-build Python installation | Passed: manifest bytes, root ownership and non-writable modes verified |
| Actual packaged shell launcher | Passed: protected Python starts the CLI and reports 2.0.0 |
| Free-build persistent sealed broker | Passed: repeated live status requests, with missing permissions reported correctly |
| Developer ID app and DMG notarization | Accepted; both tickets stapled and validated |
| Gatekeeper execution and disk-image opening | Both accepted as Notarized Developer ID |
| Notarized payload installation | Default signature policy passed; isolated install/update/rollback/uninstall passed |

Simulation uses temporary prefixes and does not install a live LaunchAgent or grant permissions. The protected runtime and broker rows above are separate live checks. Actual permission continuity remains pending; signature continuity alone does not prove it.

Final local preview: `dist/local-preview/RemCTL Capability Host.app`. Built by the actual `--from-source` command with the normal persistent key directory, whose directory/files were verified as owner-only. Packaged UI, plugin configuration, icon, installers and license notices match the checked-in inputs. `--bootstrap` now starts guided onboarding after installation when run in an interactive Terminal; redirected and test runs remain noninteractive.

## Remaining release gates

- Grant permissions to a local certificate build, change/rebuild it with the same key, and verify the grants still work. Do not infer this from designated-requirement checks alone.
- Complete administrator installation of the Developer ID build's separately signed Python runtime and its live permission checks. The free-build runtime is already installed and verified.
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

The initial M5 and M3 Ultra checks found the same Apple Development identity and no usable Developer ID identity. The M3 was checked through its saved Screen Sharing connection because SSH authentication was unavailable. After Federico approved creation, Xcode on the M5 created Developer ID Application for team `4W35M4UN6R`, certificate SHA-1 `4F0E9E16BE3065B93E959199C1A4EFA21041C80A`. The existing MacStories App Store Connect credential submitted both artifacts without exporting its key.

## Notarized local artifact

Final artifact: `dist/release-arm64/RemCTL-arm64.dmg` (43 MB).

- App submission: `b9e3cd9e-af68-479d-ab96-5a6e844e62c1`, Accepted.
- DMG submission: `b7ef703e-1bb7-4415-af29-de6aba567a2a`, Accepted.
- SHA-256: `43631c54ea9e662de6fff89141f190c15ba9fd520f06a4166787067d41c13fd9`.
- `stapler validate` passes for both app and DMG.
- `spctl --assess --type execute` accepts the app.
- `spctl --assess --type open --context context:primary-signature` accepts the DMG.

The first notarized DMG was unsigned: Apple accepted it, but Gatekeeper's disk-image opening check rejected it. The packaging script now signs the DMG with the app's exact Developer ID certificate before submitting it, verifies the publisher, and requires the disk-image opening assessment before reporting success. Use the final `dist/release-arm64` artifact, not the earlier image in `dist/developer-id-arm64`.

For permission acceptance, launch the host through its LaunchAgent. A host directly spawned by the development client can make macOS attribute a new Reminders request to that client. No ChatGPT permission was granted during that discovery. A temporary test LaunchAgent now runs the free build, separate from the existing installed host. A changed app at `dist/local-update-check` has a different code hash and the identical persistent signing requirement, ready for the real permission continuity check.
