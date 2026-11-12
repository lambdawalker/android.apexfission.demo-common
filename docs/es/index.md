# Integración de Demo Common

Esta es la guía de Desarrollo. Consulta la [instalación confirmada](../../IMPORT.md)
para ver las coordenadas de las versiones públicas y sus commits de origen.
Selecciona una versión confirmada en el sitio de documentación para leer su guía
archivada; Desarrollo describe la copia de trabajo actual. Las guías históricas
conservan sus propias identidades de código fuente y documentación. Demo Common
ofrece un catálogo Compose Material 3 para Android API 28 o superior.

| Tarea | API |
| --- | --- |
| Mostrar una bienvenida y una lista desplazable | `DemoScreen` |
| Organizar contenido personalizado en una tarjeta elevada | `DemoCard` |
| Mostrar un encabezado con metadatos e icono opcionales | `CardTitle` |

Empieza con la [guía rápida](quickstart.md) y consulta los valores predeterminados
en el [contrato de API](api.md). La aplicación anfitriona controla la navegación,
el estado, las cadenas localizadas y las acciones. Los componentes leen el tema
Material 3 activo y no realizan operaciones de entrada o salida.
