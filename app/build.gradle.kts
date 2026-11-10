plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.apexfission.android.democommon.sample"
    compileSdk { version = release(37) }
    defaultConfig {
        applicationId = namespace
        minSdk = 28
        targetSdk = 37
    }
    buildFeatures { compose = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
kotlin { jvmToolchain(17) }

dependencies {
    implementation(project(":demo-common"))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
}
