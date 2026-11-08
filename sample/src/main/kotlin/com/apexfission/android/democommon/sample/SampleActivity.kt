package com.apexfission.android.democommon.sample

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import com.apexfission.android.democommon.DemoCard
import com.apexfission.android.democommon.DemoScreen

class SampleActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val typography = Typography()
            MaterialTheme(
                colorScheme = if (isSystemInDarkTheme()) darkColorScheme() else lightColorScheme(),
                typography = typography.copy(
                    headlineLarge = typography.headlineLarge.copy(fontWeight = FontWeight.Bold),
                    titleLarge = typography.titleLarge.copy(fontWeight = FontWeight.SemiBold),
                ),
            ) {
                var showDetails by rememberSaveable { mutableStateOf(false) }
                DemoScreen(stringResource(R.string.app_name), stringResource(R.string.welcome_note)) {
                    item(key = "interactive") {
                        DemoCard(
                            title = stringResource(R.string.demo_title),
                            description = stringResource(R.string.demo_note),
                            actionLabel = stringResource(R.string.demo_action),
                            onClick = { showDetails = !showDetails },
                        )
                    }
                    if (showDetails) {
                        item(key = "details") { Text(stringResource(R.string.demo_details)) }
                    }
                }
            }
        }
    }
}
