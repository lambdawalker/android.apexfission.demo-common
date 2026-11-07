package com.apexfission.android.democommon

import android.content.res.Configuration
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.android.tools.screenshot.PreviewTest

@PreviewTest
@Preview(name = "populated-light", widthDp = 393, heightDp = 740, locale = "en")
@Preview(name = "populated-dark", widthDp = 393, heightDp = 740, locale = "en", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(name = "populated-narrow-large", widthDp = 320, heightDp = 640, locale = "es", fontScale = 1.6f)
@Composable
fun PopulatedCatalogScreenshot() {
    DemoCatalogFixture(populated = true)
}

@PreviewTest
@Preview(name = "empty-light", widthDp = 393, heightDp = 740, locale = "en")
@Preview(name = "empty-dark", widthDp = 393, heightDp = 740, locale = "en", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
fun EmptyCatalogScreenshot() {
    DemoCatalogFixture(populated = false)
}
