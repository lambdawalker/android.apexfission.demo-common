# Demo Common integration

This guide documents the confirmed **0.1.2** release of Demo Common, a
Material 3 Compose catalog for Android API 28 and higher. See
[installation instructions](../../IMPORT.md) for the coordinates for this
publication destination and [release provenance](../releases.md) for the
Maven Central/JitPack source comparison.

| Task | API |
| --- | --- |
| Show a welcome message and scrollable list | `DemoScreen` |
| Lay out custom content in an elevated card | `DemoCard` |
| Show a heading with optional metadata and icon | `CardTitle` |

Start with the [quickstart](quickstart.md) and see the [API contract](api.md)
for defaults. Keep navigation, state, localized strings, and actions in the
host app. The components read the active Material 3 theme and perform no I/O.
