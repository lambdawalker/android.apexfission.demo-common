buildscript {
    dependencies {
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.4.20")
    }
}

plugins {
    id("com.android.library") version "9.4.1" apply false
    id("com.android.application") version "9.4.1" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.4.20" apply false
    id("com.android.compose.screenshot") version "0.0.1-alpha16" apply false
    id("com.vanniktech.maven.publish") version "0.37.0" apply false
}

listOf("generateImportDocs" to "generate", "verifyImportDocs" to "verify").forEach { (taskName, command) ->
    tasks.register<Exec>(taskName) {
        group = "documentation"
        workingDir(rootDir)
        commandLine("android-repo-setup", "module_release", command)
    }
}
