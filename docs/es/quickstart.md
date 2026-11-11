# Apexfission Demo Common

Componentes Compose Material 3 reutilizables extraídos de la
[pantalla de bienvenida de Card Detector](https://github.com/lambdawalker/android.apexfission.carddetector/blob/main/app/src/main/java/com/apexfission/android/carddetector/demo/WelcomeActivity.kt).

## Requisitos e instalación

La biblioteca está diseñada para Compose Material 3 y Android API 28 o posterior.
Compilar este repositorio requiere Android SDK 37 y JDK 17. CI ejecuta Gradle con
JDK 21. La biblioteca no requiere configurar permisos, navegación ni ciclo de vida.

Para usar dependencias públicas, elige un destino y una sintaxis de dependencia en
las [instrucciones de instalación confirmadas](../../IMPORT.md). Cada destino
tiene su propia versión confirmada y su commit de origen; usa esas coordenadas
juntas.

Esta guía de Desarrollo describe la copia de trabajo actual. Para una versión
publicada, selecciona su documentación archivada y su identidad de código fuente
en el sitio de documentación. Las instrucciones de instalación más recientes
pueden apuntar a una versión posterior a la de una guía archivada. Solo se publica
la variante `release` de la biblioteca.

Para probar cambios de esta copia de trabajo localmente, publica en Maven Local:

```shell
./gradlew :demo-common:publishToMavenLocal
```

Agrega `mavenLocal()` a los repositorios de dependencias del proyecto consumidor
y usa la versión configurada para esa publicación local. Publicar localmente no
confirma una versión pública. Consulta el [manual de publicación](../releases.md)
para configurar la publicación.

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
