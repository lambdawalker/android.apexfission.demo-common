import com.vanniktech.maven.publish.AndroidSingleVariantLibrary
import com.vanniktech.maven.publish.JavadocJar
import com.vanniktech.maven.publish.SourcesJar

plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.plugin.compose")
    id("com.android.compose.screenshot")
    id("com.vanniktech.maven.publish")
}

android {
    namespace = "com.apexfission.android.democommon"
    compileSdk {
        version = release(37)
    }
    defaultConfig {
        minSdk = 28
    }
    buildFeatures {
        compose = true
    }
    experimentalProperties["android.experimental.enableScreenshotTest"] = true
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    api(platform("androidx.compose:compose-bom:2026.09.00"))
    api("androidx.compose.foundation:foundation")
    api("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")

    debugImplementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")
    screenshotTestImplementation("com.android.tools.screenshot:screenshot-validation-api:0.0.1-alpha16")
    screenshotTestImplementation("androidx.compose.ui:ui-tooling")
}

val releaseVersion = providers.gradleProperty("releaseVersion")
val projectUrl = "https://github.com/lambdawalker/android.apexfission.demo-common"
mavenPublishing {
    coordinates("com.apexfission.android", "demo-common", releaseVersion.getOrElse("0.0.0-SNAPSHOT"))
    configure(AndroidSingleVariantLibrary(
        variant = "release",
        javadocJar = JavadocJar.Empty(),
        sourcesJar = SourcesJar.Sources(),
    ))
    if (releaseVersion.isPresent) {
        require(releaseVersion.get().matches(Regex("(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)"))) {
            "releaseVersion must be a stable semantic version such as 0.1.0"
        }
        publishToMavenCentral()
        signAllPublications()
    }
    pom {
        name.set("Apexfission Demo Common")
        description.set("Reusable Material 3 Compose components for Android demo catalogs.")
        url.set(projectUrl)
        licenses {
            license {
                name.set("The Apache License, Version 2.0")
                url.set("https://www.apache.org/licenses/LICENSE-2.0.txt")
            }
        }
        developers {
            developer {
                id.set("lambdawalker")
                name.set("David Garcia")
            }
        }
        scm {
            url.set(projectUrl)
            connection.set("scm:git:$projectUrl.git")
            developerConnection.set("scm:git:ssh://git@github.com/lambdawalker/android.apexfission.demo-common.git")
        }
    }
}
