# Compose API

Import these declarations from `com.apexfission.android.democommon`. Call
them from an existing Material 3 composition. Each accepts the caller's
`Modifier` and returns `Unit`.

## DemoScreen

```kotlin
@Composable
public fun DemoScreen(
    title: String,
    welcomeNote: String,
    modifier: Modifier = Modifier,
    eyebrow: String? = null,
    maxContentWidth: Dp = 640.dp,
    contentPadding: PaddingValues = PaddingValues(24.dp),
    contentWindowInsets: WindowInsets = ScaffoldDefaults.contentWindowInsets,
    itemSpacing: Dp = 16.dp,
    showEmptyState: Boolean = false,
    onOpenSettings: (() -> Unit)? = null,
    content: LazyListScope.() -> Unit = {},
)
```

Provide localized text and declare cards with `item` or `items`. Use stable
keys for changing lists. The screen fills available bounds, combines Scaffold
`contentWindowInsets` with `contentPadding` without clipping edge-to-edge
scrolling, and centers its lazy column within the configured maximum width.
Set `showEmptyState = true` when there are no demos. The empty panel uses
the host’s Material 3 theme and localized library strings. Supply
`onOpenSettings` to add a full-width App settings button below the header and before the demo cards
or empty panel. The host callback owns navigation, such as opening Android’s
app details settings. Give this screen bounded height and avoid nesting it in
a vertically scrolling parent.

## DemoCard

```kotlin
@Composable
public fun DemoCard(
    modifier: Modifier = Modifier,
    contentPadding: PaddingValues = PaddingValues(20.dp),
    itemSpacing: Dp = 12.dp,
    content: @Composable ColumnScope.() -> Unit,
)
```

The card fills the available width and uses the host Material 3 card defaults.
Content owns interaction state, accessibility labels, and callbacks.
Use a Material button in the content slot to open the selected demo.

For the standard welcome catalog card, call the overload with `title`,
`description`, `actionLabel`, and `onClick`. It renders a `CardTitle` with
an optional `icon`, followed by the description and a
full-width filled tonal button. Use the content slot above for custom cards.

```kotlin
@Composable
public fun DemoCard(
    title: String,
    description: String,
    actionLabel: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
)
```

## CardTitle

```kotlin
@Composable
public fun CardTitle(
    title: String,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
)
```

The title has heading semantics for TalkBack. The icon is decorative. Put essential status information in the text. The theme
provides typography and colors. There are no callbacks, background tasks,
Android permissions, or resources to close.

The host app supplies colors, shapes, and typography through `MaterialTheme`.
`DemoScreen` uses `headlineLarge` for its heading, and `CardTitle` uses
`titleLarge`. Set the weights on those styles in the host theme to reproduce
the bold screen heading and semibold card title of the welcome example.
