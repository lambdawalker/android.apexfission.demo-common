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
val releaseModule = providers.gradleProperty("releaseModule")
val jitpackBuild = providers.gradleProperty("jitpackBuild").map(String::toBoolean).getOrElse(false)
val groupId = providers.gradleProperty("GROUP").get()
val artifactId = providers.gradleProperty("POM_ARTIFACT_ID").get()
val repositoriesConfig = java.util.Properties().apply {
    rootProject.file("publishing/repositories.properties").inputStream().use { load(it) }
}
val destination = providers.environmentVariable("RELEASE_REPOSITORY").getOrElse("maven-central")
val publisher = repositoriesConfig.getProperty("$destination.publisher")
require(publisher in setOf("central", "jitpack")) { "Unknown release destination" }
if (releaseVersion.isPresent) {
    require(releaseModule.orNull == name) { "Select -PreleaseModule=demo-common for a release" }
}
if (jitpackBuild) {
    require(releaseVersion.isPresent && providers.gradleProperty("jitpackScopedTag").orNull == "true") {
        "A destination-scoped JitPack release identity is required"
    }
}

val projectUrl = "https://github.com/lambdawalker/android.apexfission.demo-common"
mavenPublishing {
    val version = releaseVersion.getOrElse("0.0.0-SNAPSHOT")
    coordinates(
        if (jitpackBuild) "com.github.lambdawalker" else groupId,
        if (jitpackBuild) rootProject.name else artifactId,
        if (jitpackBuild) "demo-common~v$version-jitpack" else version,
    )
    configure(AndroidSingleVariantLibrary(
        variant = "release",
        javadocJar = JavadocJar.Empty(),
        sourcesJar = SourcesJar.Sources(),
    ))
    if (releaseVersion.isPresent) {
        require(releaseVersion.get().matches(Regex("(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)"))) {
            "releaseVersion must be a stable semantic version such as 0.1.0"
        }
        if (!jitpackBuild && publisher == "central") {
            publishToMavenCentral()
            if (providers.gradleProperty("signingInMemoryKey").isPresent) signAllPublications()
        }
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

tasks.withType<com.vanniktech.maven.publish.tasks.JavadocJar>().configureEach {
    from(rootProject.file("LICENSE"))
    from(rootProject.file("docs/releases.md"))
    from(rootProject.file("docs/agents")) { into("agents") }
}

tasks.withType<org.gradle.jvm.tasks.Jar>().configureEach {
    isPreserveFileTimestamps = false
    isReproducibleFileOrder = true
}

extensions.configure<org.gradle.api.publish.PublishingExtension> {
    repositories.maven {
        name = "verification"
        url = rootProject.layout.buildDirectory.dir("verification-repository").get().asFile.toURI()
    }
}

val verifyPublicationReservation by tasks.registering(Exec::class) {
    workingDir(rootDir)
    commandLine("python3", "scripts/module_release.py", "guard",
        "--module", project.name, "--version", releaseVersion.getOrElse(""))
    doFirst {
        require(!jitpackBuild && publisher == "central" && releaseModule.orNull == project.name) {
            "Maven Central upload requires the selected library and a Central reservation"
        }
        listOf("mavenCentralUsername", "mavenCentralPassword", "signingInMemoryKey").forEach {
            require(!providers.gradleProperty(it).orNull.isNullOrBlank()) { "Missing release credential: $it" }
        }
    }
}

tasks.matching { it.name.contains("MavenCentral", ignoreCase = true) }.configureEach {
    dependsOn(verifyPublicationReservation)
}
