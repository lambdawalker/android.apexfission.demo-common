# Integración de Demo Common

Esta guía documenta la versión confirmada **0.1.2** de Demo Common, un
catálogo Compose Material 3 para Android API 28 o superior. Consulta las
[instrucciones de instalación](../../IMPORT.md) para ver las coordenadas de
este destino de publicación y la [procedencia de la versión](../releases.md)
para comparar el código de origen en Maven Central y JitPack.

| Tarea | API |
| --- | --- |
| Mostrar una bienvenida y una lista desplazable | `DemoScreen` |
| Organizar contenido personalizado en una tarjeta elevada | `DemoCard` |
| Mostrar un encabezado con metadatos e icono opcionales | `CardTitle` |

Empieza con la [guía rápida](quickstart.md) y consulta los valores predeterminados
en el [contrato de API](api.md). La aplicación anfitriona controla la navegación,
el estado, las cadenas localizadas y las acciones. Los componentes leen el tema
Material 3 activo y no realizan operaciones de entrada o salida.
