pluginManagement {
    resolutionStrategy {
        eachPlugin {
            if (requested.id.id in setOf(
                    "com.apexfission.android-repo-setup",
                    "com.apexfission.android-repo-setup.root",
                )
            ) {
                requested.version?.let { version ->
                    useModule("com.github.lambdawalker:gradle.android-repo-setup:$version")
                }
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
include(":app")
