# Guía rápida

Agrega la dependencia que aparece en la [instalación confirmada](../../IMPORT.md).
Durante el desarrollo puedes ejecutar `./gradlew :demo-common:publishToMavenLocal`,
agregar `mavenLocal()` al proyecto anfitrión y usar la dependencia
`com.apexfission.android:demo-common:0.0.0-SNAPSHOT`.

Llama a `DemoScreen` dentro de un tema Material 3. Pasa el título y la nota
de bienvenida desde los recursos de la aplicación. Declara cada tarjeta con
`item` o usa `items` para una lista con claves estables. Dentro de
`DemoCard` agrega el título, el texto y los botones que necesites.
La [referencia de API](api.md) enumera los parámetros.

## Ejecutar el ejemplo

Inicia un emulador Android API 28 o superior, o conecta un dispositivo.
Ejecuta `./gradlew :app:installDebug` y abre **Ejemplo de Demo Common**.
Toca **Alternar detalles** para mostrar u ocultar el contenido adicional.
Cambia el idioma o el tema del dispositivo para probar las traducciones
y los colores.

La [actividad de ejemplo](../../app/src/main/kotlin/com/apexfission/android/democommon/sample/SampleActivity.kt)
contiene la integración completa.

El botón de ajustes aparece debajo del encabezado y antes de las tarjetas o del panel vacío. La aplicación anfitriona sigue controlando su navegación.
