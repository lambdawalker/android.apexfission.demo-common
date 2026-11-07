# Referencia de API

Importa los componentes de `com.apexfission.android.democommon`.
Cada componente recibe un `Modifier` y devuelve `Unit`.

## DemoScreen

Requiere `title` y `welcomeNote`. `eyebrow` agrega una etiqueta opcional
sobre el título. El ancho máximo predeterminado es 640 dp, con 24 dp de
margen interno y 16 dp entre elementos. Declara el contenido mediante
`LazyListScope`. Sin elementos se muestra el encabezado. Proporciona
una altura acotada y evita anidarlo dentro de otro contenedor de
desplazamiento vertical.

## DemoCard

Recibe un bloque de contenido `ColumnScope`. Usa el ancho disponible,
la forma mediana del tema, 20 dp de margen interno y 12 dp de separación
por defecto. La aplicación controla los botones y su estado.

## CardTitle

Requiere `title` y admite `subtitle` e `icon`. El título se anuncia como
encabezado y el icono es decorativo. Coloca cualquier información esencial
en texto. La aplicación anfitriona proporciona el tema y el contenido.
