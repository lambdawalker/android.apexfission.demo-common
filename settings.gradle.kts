pluginManagement {
    val releasePluginBuild = providers.environmentVariable("ANDROID_REPO_SETUP_GRADLE_DIR")
        .orElse("../gradle.android-repo-setup")
    includeBuild(releasePluginBuild.get())
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
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
