# Apexfission Demo Common

Componentes Compose Material 3 reutilizables extraídos de la
[pantalla de bienvenida de Card Detector](https://github.com/lambdawalker/android.apexfission.carddetector/blob/main/app/src/main/java/com/apexfission/android/carddetector/demo/WelcomeActivity.kt).

## Requisitos e instalación

La biblioteca está diseñada para Compose Material 3 y Android API 28 o posterior.
Compilar este repositorio requiere Android SDK 37 y JDK 17. CI ejecuta Gradle con
JDK 21. La biblioteca no requiere configurar permisos, navegación ni ciclo de vida.

Usa la versión confirmada **0.1.2** de Maven Central o JitPack. Consulta las
[instrucciones de instalación](../../IMPORT.md) para configurar el repositorio
y obtener las coordenadas exactas del destino seleccionado. Ambos destinos
contienen binarios y código fuente idénticos de la biblioteca; sus commits de
publicación solo difieren en metadatos. Consulta la
[procedencia de la versión](../releases.md).

Maven Central:

```kotlin
implementation("com.apexfission.android:demo-common:0.1.2")
```

JitPack:

```kotlin
implementation("com.github.lambdawalker:android.apexfission.demo-common:demo-common~v0.1.2-jitpack")
```

Solo se publica la variante `release` de la biblioteca. En la versión 0.1.2,
el botón opcional de ajustes aparece después del contenido personalizado del
catálogo. Su posición encima de las tarjetas corresponde a cambios posteriores
de desarrollo y no forma parte de esta versión.

## Declarar un catálogo de demostraciones

Llama a los componentes desde un tema Material 3 existente. Pasa las cadenas
localizadas de la aplicación consumidora. Proporciona tus propias acciones y
funciones de navegación.

```kotlin
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.apexfission.android.democommon.CardTitle
import com.apexfission.android.democommon.DemoCard
import com.apexfission.android.democommon.DemoScreen

@Composable
fun ExampleCatalog(onOpenExample: () -> Unit) {
    DemoScreen(
        title = "Demo catalog",
        welcomeNote = "Choose an example to get started.",
        eyebrow = "EXAMPLES",
    ) {
        item(key = "example") {
            DemoCard {
                CardTitle(title = "Interactive example")
                Text("Try the example with your own input.")
                FilledTonalButton(
                    onClick = onOpenExample,
                    modifier = Modifier.fillMaxWidth(),
                    shape = MaterialTheme.shapes.small,
                ) {
                    Text("Open example")
                }
            }
        }
    }
}
```

`DemoScreen` usa el DSL estándar de `LazyListScope`, por lo que permite declarar
elementos individuales, listas con claves y pies de página. `DemoCard` acepta un
bloque `ColumnScope` con cualquier contenido Compose. Usa `CardTitle` dentro o
fuera de una tarjeta, con un icono decorativo opcional. La pantalla y la tarjeta
permiten personalizar los márgenes internos y la separación; la pantalla también
acepta un ancho máximo de contenido.

## Cobertura de vistas previas y capturas de pantalla

El catálogo con contenido prueba `DemoScreen`, `DemoCard` y `CardTitle`, con un
icono en la primera tarjeta y solo un título en la segunda. El catálogo vacío
prueba `DemoScreen` con su panel vacío adaptado al tema y el botón de ajustes de
la aplicación. El catálogo con contenido también muestra el botón de ajustes
debajo del encabezado y encima de las tarjetas. Ambos escenarios cubren los modos
claro y oscuro con un tema anfitrión de prueba que personaliza colores,
tipografía y formas. Una vista previa estrecha de 320 dp, con escala de fuente
1.6×, comprueba los saltos de línea con un título de tarjeta, una descripción y
una acción largos en español.

```shell
./gradlew :demo-common:assembleRelease :demo-common:lintDebug
./gradlew :demo-common:updateDebugScreenshotTest
./gradlew :demo-common:validateDebugScreenshotTest
```

Usa la tarea de actualización para generar las capturas candidatas. Revisa los
cinco PNG de `demo-common/src/screenshotTestDebug/reference/` antes de incluirlos
en un commit como imágenes de referencia. Una vez incluidos, CI usa la tarea de
validación y sube los informes y un manifiesto de sumas de comprobación de las
imágenes. Hasta entonces, CI genera las capturas candidatas y comprueba que se
hayan generado las cinco imágenes.

## Ejecutar el ejemplo

Con un emulador API 28 o superior o un dispositivo conectado, ejecuta
`./gradlew :app:installDebug` y abre **Ejemplo de Demo Common**. Toca
**Alternar detalles** para mostrar u ocultar texto dentro de la tarjeta. Cambia
el tema o el idioma del dispositivo para probar los colores claros y oscuros y
las cadenas en inglés y español. La
[actividad de ejemplo](../../app/src/main/kotlin/com/apexfission/android/democommon/sample/SampleActivity.kt)
contiene la integración completa.
