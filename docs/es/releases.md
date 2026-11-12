# Procedencia de Demo Common 0.1.2

## Código fuente publicado

| Destino | Versión de consumo | Commit de origen inmutable |
| --- | --- | --- |
| Maven Central | `0.1.2` | [`11d3cdce31c4`](https://github.com/lambdawalker/android.apexfission.demo-common/commit/11d3cdce31c481fe2204f00d25b5fd93e5f9a18c) |
| JitPack | `demo-common~v0.1.2-jitpack` | [`86b43bd7ee85`](https://github.com/lambdawalker/android.apexfission.demo-common/commit/86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f) |

Los commits son distintos, pero el código de la biblioteca y la configuración
de compilación son idénticos. El commit de origen de Central solo agrega
`IMPORT.md`, el registro confirmado de JitPack y su confirmación archivada.
No cambia el código de la biblioteca.

## Artefactos verificados

Se descargaron el AAR, el archivo de código fuente y el archivo Javadoc públicos
de ambos destinos y se compararon con los registros de confirmación. Cada par
correspondiente contiene exactamente los mismos bytes:

| Artefacto | SHA-256 en ambos destinos |
| --- | --- |
| `.aar` | `b2e86d8f0693fef318e7469414ac877b773204f49073d8e52f1df72e403aa5d2` |
| `-sources.jar` | `c86a2894e289e023d084805ed52e1af177ec85edcc12e728bc40cbe60dbff2a6` |
| `-javadoc.jar` | `ca4b749dcab38bb14fb0e24bfa873fd17aeee209beb2722e7a1b63aae82e9276` |

Los hashes registrados del POM y de los metadatos de módulo de Gradle son
distintos porque los proveedores usan coordenadas de publicación diferentes.
La igualdad de los archivos de la biblioteca no convierte los commits de Git
en uno solo; se conservan ambas etiquetas de origen y sus registros de
confirmación. Esta documentación corregida se aplica a ambas publicaciones de
la versión 0.1.2 sin cambiar sus identidades de publicación.

## Comportamiento publicado

El botón opcional de ajustes aparece después del contenido personalizado del
catálogo en 0.1.2. Su posición encima de las tarjetas corresponde a un cambio
posterior de desarrollo. Estas guías y capturas describen el comportamiento
publicado y no la copia de trabajo actual. Usa las
[instrucciones de instalación confirmadas](../IMPORT.md) para las dependencias.

## Mantenimiento de versiones

Consulta los procedimientos actuales de configuración, publicación y recuperación
en el [manual de mantenimiento](https://github.com/lambdawalker/android.apexfission.demo-common/blob/main/docs/releases.md).
Las versiones nuevas usan una identidad de publicación inmutable compartida
entre proveedores; esa regla no se aplica retroactivamente a estos commits.
