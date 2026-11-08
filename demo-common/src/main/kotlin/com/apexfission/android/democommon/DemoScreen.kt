package com.apexfission.android.democommon

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.calculateEndPadding
import androidx.compose.foundation.layout.calculateStartPadding
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListScope
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.ScaffoldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * A centered, scrolling catalog with a caller-provided [title] and [welcomeNote].
 *
 * Declare cards or footers with [content]. Set [showEmptyState] when there are no demos.
 * Supply [onOpenSettings] to offer the App settings action in either state.
 * The screen combines its scaffold's [contentWindowInsets] with [contentPadding] and
 * consumes those insets so edge-to-edge scrolling is not clipped.
 */
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
) {
    Scaffold(
        modifier = modifier,
        contentWindowInsets = contentWindowInsets,
    ) { insets ->
        val layoutDirection = LocalLayoutDirection.current
        val combinedPadding = PaddingValues(
            start = insets.calculateStartPadding(layoutDirection) + contentPadding.calculateStartPadding(layoutDirection),
            top = insets.calculateTopPadding() + contentPadding.calculateTopPadding(),
            end = insets.calculateEndPadding(layoutDirection) + contentPadding.calculateEndPadding(layoutDirection),
            bottom = insets.calculateBottomPadding() + contentPadding.calculateBottomPadding(),
        )
        Box(
            modifier = Modifier.fillMaxSize().consumeWindowInsets(insets),
            contentAlignment = Alignment.TopCenter,
        ) {
            LazyColumn(
                modifier = Modifier.widthIn(max = maxContentWidth).fillMaxSize(),
                contentPadding = combinedPadding,
                verticalArrangement = Arrangement.spacedBy(itemSpacing),
            ) {
                item(key = "demo_screen_header", contentType = "header") {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        eyebrow?.let {
                            Text(
                                text = it,
                                style = MaterialTheme.typography.labelLarge,
                                color = MaterialTheme.colorScheme.primary,
                            )
                        }
                        Text(
                            text = title,
                            modifier = Modifier.semantics { heading() },
                            style = MaterialTheme.typography.headlineLarge,
                        )
                        if (!showEmptyState) {
                            Text(
                                text = welcomeNote,
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                }
                content()
                if (onOpenSettings != null) {
                    item {
                        OutlinedButton(onClick = onOpenSettings, modifier = Modifier.fillMaxWidth()) {
                            Icon(
                                painter = painterResource(R.drawable.demo_common_settings),
                                contentDescription = null,
                                modifier = Modifier.size(18.dp),
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(stringResource(R.string.demo_common_app_settings))
                        }
                    }
                }
                if (showEmptyState) {
                    item { DemoCatalogEmptyState() }
                }
            }
        }
    }
}

@Composable
private fun DemoCatalogEmptyState() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        color = MaterialTheme.colorScheme.secondaryContainer,
        contentColor = MaterialTheme.colorScheme.onSecondaryContainer,
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 24.dp, vertical = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.demo_common_empty_title),
                modifier = Modifier.semantics { heading() },
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center,
            )
            Text(
                text = stringResource(R.string.demo_common_empty_note),
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
            )
        }
    }
}
