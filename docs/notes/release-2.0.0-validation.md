# RemCTL 2.0 release validation

September 30, 2026. Apple silicon release built from `release/2.0.0`, application source commit `b705a9c`.

## Redesigned signed artifact

This build supersedes the earlier `ec32a0e` distribution artifact. The previous notarization receipts in [distribution validation](distribution-validation-2026-09-30.md) cover the older workspace, not this redesign.

- Build directory: `dist/release-2.0.0-arm64`.
- Plugin build: `912f82237323316f`.
- Workspace SHA-256: `740c62eee4a4dcf5de35a2b03cb70f387d05f2b94e8462e689632abde4c560f0`.
- App submission: `875b4d08-e8c7-4faf-b5e0-69004c00cf11` (Accepted).
- DMG submission: `4967bedb-980c-4bf1-850f-ed70f9955f86` (Accepted).
- DMG SHA-256: `bd22e3de8b436003a2bed21ddc2c7310b5b0883be7eec476b519f9ff11c9e9ef`.
- Signing: MacStories Developer ID, team `4W35M4UN6R`.

The app and disk image have stapled tickets. Strict nested signature verification, ticket validation, and Gatekeeper app execution and disk-image opening all passed. The disk image mounted read-only; its app signature passed, and the packaged workspace matched the release branch byte for byte. Server modules and plugin manifests also match source.

The complete Python suite ran 844 tests successfully, with 6 skipped. TypeScript checks, interaction tests, SDK contracts, and the production UI build passed. Rebuilding the UI left its committed bundle and plugin build identifier unchanged.

## Installed acceptance

Pending completion of the protected runtime installation and native workspace checks.

## Publication boundary

No tag or GitHub release has been created. The public download remains unavailable until the release is published. Apple silicon is the release target.
