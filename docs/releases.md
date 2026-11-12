# Demo Common 0.1.2 release provenance

## Published sources

| Destination | Consumer version | Immutable source commit |
| --- | --- | --- |
| Maven Central | `0.1.2` | [`11d3cdce31c4`](https://github.com/lambdawalker/android.apexfission.demo-common/commit/11d3cdce31c481fe2204f00d25b5fd93e5f9a18c) |
| JitPack | `demo-common~v0.1.2-jitpack` | [`86b43bd7ee85`](https://github.com/lambdawalker/android.apexfission.demo-common/commit/86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f) |

The commits are different, but their library code and build configuration are
identical. The Central source commit adds only `IMPORT.md`, the confirmed
JitPack record, and its archived confirmation. It does not change library code.

## Verified artifacts

The public AAR, source archive and Javadoc archive were downloaded from both
destinations and checked against their confirmation records. Each corresponding
pair is byte-identical:

| Artifact | SHA-256 at both destinations |
| --- | --- |
| `.aar` | `b2e86d8f0693fef318e7469414ac877b773204f49073d8e52f1df72e403aa5d2` |
| `-sources.jar` | `c86a2894e289e023d084805ed52e1af177ec85edcc12e728bc40cbe60dbff2a6` |
| `-javadoc.jar` | `ca4b749dcab38bb14fb0e24bfa873fd17aeee209beb2722e7a1b63aae82e9276` |

POM and Gradle module metadata have different recorded hashes because the
providers use different publication coordinates. Equal library payloads do not
make the two Git commits identical, so both source tags and confirmation records
remain separate. This corrected documentation applies to both publications of
version 0.1.2 without changing their release identities.

## Released behavior

The optional App settings button follows custom catalog content in 0.1.2.
Moving it above the demo cards is a later development change. These guides and
screenshots describe the published behavior rather than the current checkout.
Use the [confirmed installation instructions](../IMPORT.md) for dependencies.

## Maintaining releases

For current setup, publishing and recovery procedures, see the
[maintainer runbook](https://github.com/lambdawalker/android.apexfission.demo-common/blob/main/docs/releases.md).
New versions use a shared immutable release identity across providers; that rule
is not retroactively applied to these historical commits.
