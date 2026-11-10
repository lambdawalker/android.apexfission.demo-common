pluginManagement {
    val releasePluginVersion = "v0.1.4"
    resolutionStrategy {
        eachPlugin {
            if (requested.id.id in setOf(
                    "com.apexfission.android-repo-setup",
                    "com.apexfission.android-repo-setup.root",
                )
            ) {
                useModule("com.github.lambdawalker:gradle.android-repo-setup:$releasePluginVersion")
            }
        }
    }
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        maven("https://jitpack.io") {
            content { includeModule("com.github.lambdawalker", "gradle.android-repo-setup") }
        }
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "android.apexfission.demo-common"
include(":demo-common")
include(":sample")
