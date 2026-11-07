# Compose API

Import these declarations from `com.apexfission.android.democommon`. Call
them from an existing Material 3 composition. Each accepts the caller's
`Modifier` and returns `Unit`.

```kotlin
@Composable
fun DemoScreen(
    title: String,
    welcomeNote: String,
    modifier: Modifier = Modifier,
    eyebrow: String? = null,
    maxContentWidth: Dp = 640.dp,
    contentPadding: PaddingValues = PaddingValues(24.dp),
    itemSpacing: Dp = 16.dp,
    content: LazyListScope.() -> Unit,
)
```

Provide localized text and declare cards with `item` or `items`. Use stable
keys for changing lists. The screen fills available bounds, applies Scaffold
insets, then centers its lazy column within the configured maximum width.
An empty slot displays the header. Give this screen bounded height and avoid
nesting it in a vertically scrolling parent.

```kotlin
@Composable
fun DemoCard(
    modifier: Modifier = Modifier,
    contentPadding: PaddingValues = PaddingValues(20.dp),
    itemSpacing: Dp = 12.dp,
    content: @Composable ColumnScope.() -> Unit,
)
```

The card fills the available width and uses the host's medium shape.
Content owns interaction state, accessibility labels, and callbacks.
Use a Material button in the content slot to open the selected demo.

```kotlin
@Composable
fun CardTitle(
    title: String,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    icon: ImageVector? = null,
)
```

The title has heading semantics. The subtitle is optional and the icon
is decorative. Put essential status information in the text. The theme
provides typography and colors. There are no callbacks, background tasks,
Android permissions, or resources to close.
