# Publicación de Demo Common

Solo se publica el AAR `release` de `:demo-common`. Gradle se ejecuta con JDK 21
y produce bytecode Java 17.

## Configuración del responsable

Este checkout fija la CLI con identidad compartida a un commit inmutable de las
herramientas en `.project/setup/config.yaml`. Cargo compila esa revisión una
sola vez; las siguientes ejecuciones reutilizan el ejecutable en caché. El
plugin de Gradle conserva la versión publicada `v0.1.9`. El sitio de
documentación requiere además Zola 0.23.6.

Ejecuta `setup.bat` en Windows o `./setup.sh` en Linux o macOS para abrir el
asistente de despliegue de iocraft. Usa Tab y Mayús+Tab para cambiar de control,
Espacio para marcar casillas e Intro para activar botones. Los campos de
contraseña están ocultos; Re Pág/Av Pág desplazan los formularios y
Mayús+Re Pág/Av Pág desplazan el registro de progreso. Ambos lanzadores leen `tooling_ref` de
`.project/setup/config.yaml`. Para una etiqueta de versión estable, Windows
descarga y verifica la CLI correspondiente en el primer uso y la almacena en
caché en `bin/<tag>/`. En Linux o macOS, instala esa versión exacta desde
[las versiones de Android Repository Setup](https://github.com/lambdawalker/gradle.android-repo-setup/releases),
verifica la suma de comprobación del archivo y coloca el ejecutable extraído en
`PATH`. El lanzador comprueba su versión antes de ejecutarlo. Para un SHA completo
de commit de origen, ambos lanzadores usan Cargo para compilar esa revisión
exacta una sola vez y guardan el ejecutable en caché en `bin/<SHA>/bin/`. Cargo es
necesario para instalar una revisión de código fijada; las siguientes ejecuciones
reutilizan el ejecutable en caché.

Usa un token de GitHub
limitado al repositorio con los permisos de administración de entornos indicados
por el asistente. Revisa los cambios antes de aplicarlos. Central requiere
`MAVEN_CENTRAL_USERNAME`, `MAVEN_CENTRAL_PASSWORD`, `SIGNING_IN_MEMORY_KEY`
y la contraseña de firma si corresponde. Crea una clave de firma Maven en el
asistente o selecciona una existente del llavero GnuPG local. Confirma la
propiedad del espacio de nombres en Central Portal. JitPack público usa un
entorno vacío y requiere un repositorio público en GitHub.

Configura un temporizador de espera de 15 minutos en `delayed-docs` cuando esté
disponible. En Settings → Pages, selecciona GitHub Actions. El token de
publicación debe poder enviar etiquetas de publicación y actualizaciones de
documentación confirmadas conforme a las reglas existentes. La protección de
Maven Central también actualiza su etiqueta `release-pending/*` al registrar el
marcador de subida.

## Publicar

Ejecuta **Publish Demo Common** en `main`. Elige Maven Central o JitPack y deja
**version** en blanco. Las nuevas versiones comparten un commit de origen
inmutable y una huella de las entradas de compilación entre destinos. Si las
entradas coinciden, se reutilizan esa versión del módulo y su código exacto;
si cambian, se incrementa el parche. Solo se acepta una versión compartida
existente explícita si sus entradas coinciden. Una versión explícita nueva
debe ser posterior al historial de publicación del módulo.

La primera publicación reserva atómicamente
`release-identity/demo-common/X.Y.Z` junto con el registro del destino. Publicar
la misma versión en el otro destino reutiliza esa identidad. Las etiquetas
`demo-common/vX.Y.Z-maven-central` y `demo-common/vX.Y.Z-jitpack` y sus estados
de publicación siguen siendo independientes. JitPack usa una tilde en la
versión de consumo. La firma y los metadatos pueden variar entre destinos;
no se exige que los bytes de sus artefactos sean idénticos.

La huella abarca el código de la biblioteca, las guías empaquetadas, la cadena
de herramientas, la configuración de compilación versionada y las utilidades
compartidas de publicación. Se excluyen los registros de confirmación generados
y las instrucciones de instalación. Los intentos fallidos conservan su versión
compartida inmutable; nunca la liberan para otro código fuente.

Las versiones históricas como `0.1.2` conservan sus identidades de origen por
destino. No se combinan retroactivamente. Las versiones compartidas nuevas
empiezan después del historial existente del módulo y agrupan los destinos
confirmados en una sola versión de documentación.

El flujo de trabajo valida los artefactos locales antes de reservar una versión.
Central escribe un marcador antes de subir y verifica los hashes y las firmas
públicos tras la propagación. JitPack comprueba el commit de origen de la
compilación y los artefactos públicos.
[IMPORT.md](../IMPORT.md) solo se actualiza tras la confirmación.

## Recuperación

Conserva las etiquetas canónicas, pendientes y de inicio de subida si se
interrumpe una ejecución. Inspecciona el registro de publicación y el estado del
proveedor. Ejecuta **Finalize Demo Common release** con el mismo destino y la
versión reservada. Verifica y finaliza sin volver a subir artefactos. Si la
protección de rama rechaza el envío final, conserva la reserva y pide a un
responsable de mantenimiento que la reconcilie.

Si un intento interrumpido de Central nunca llegó a publicarse y Central Portal
confirma que no existe despliegue, archiva los marcadores no confirmados
`release-pending` y `release-uploading` en `release-failed/` mediante
`android-repo-setup module_release abort-unconfirmed --module demo-common --version X.Y.Z`
(que comprueba `published_versions` en Maven Central antes de archivar).

Un fallo terminal de JitPack sin artefactos públicos se puede archivar mediante
un nuevo intento desde código corregido. Solo para JitPack, una versión
explícita posterior permite omitir intentos pendientes anteriores. Esta opción
conserva esos registros y comprueba la procedencia de su código fuente. Para
Central, la opción de recuperación solo omite la lista pública de versiones y
requiere una versión explícita posterior.

GitHub puede sustituir una ejecución anterior en cola por otra más reciente. El
bloqueo compartido del trabajo serializa las modificaciones y se libera durante
la espera de propagación. Las etiquetas de reserva conservan el estado de la
publicación con independencia de la cola.

## Verificar sin publicar

```sh
android-repo-setup publishing_config check
android-repo-setup import_docs --check
android-repo-docs build --check
android-repo-setup workflows --check
./gradlew verifyImportDocs :demo-common:testDebugUnitTest :demo-common:lintRelease :demo-common:assembleRelease
```

CI también genera publicaciones locales sin firmar para ambos destinos y valida
el AAR, el código fuente, el archivo de documentación, el POM y los metadatos de
Gradle. La compilación de Pages se ejecuta en las solicitudes de incorporación
de cambios y se despliega desde `main`, también después de finalizar una
publicación correctamente.

## Preparar la firma de un APK de demostración

Ejecuta esto desde una terminal privada con JDK. Usa `./setup.sh` en Linux o
macOS, o `setup.bat` en Windows. Ambos lanzadores usan el `tooling_ref`
configurado y siguen las reglas de instalación y caché anteriores; Git ignora
el directorio `bin/`. La CLI abre la bóveda cifrada existente sin moverla.
Para abrir directamente el asistente de firma, ejecuta `./setup.sh signing` o
`setup.bat signing`.

En el asistente de terminal, elige crear un almacén de claves, configurar GitHub
con una clave existente o ambas opciones. La primera ejecución selecciona ambas
por defecto. Las posteriores seleccionan los pasos incompletos o Salir si ambos
están completos. Las preguntas sin secretos usan una cuenta atrás de 20 segundos
hasta que escribas, pegues o hagas clic en un campo. Después de interactuar,
confirma manualmente. Si no interactúas, se aplica el valor predeterminado
mostrado. Las confirmaciones de subida, restablecimiento y revelación de
contraseñas cancelan o conservan el estado actual por defecto. Las preguntas de
contraseñas y tokens esperan una respuesta.

La bóveda de cada repositorio en
`~/.projects/android.apexfission.demo-common/secrets/` cifra el progreso de la
configuración, los datos del almacén de claves y las contraseñas de firma
verificadas. Puede recordar un token de GitHub si lo autorizas expresamente.
Desbloquea la bóveda con su contraseña independiente en cada ejecución. Perder
esa contraseña implica perder el acceso a las respuestas guardadas.
Restablecer la configuración local borra esas respuestas y conserva el almacén
de claves y los secretos de GitHub.

Usa un token de GitHub de permisos detallados limitado a este repositorio con
**Administration: read/write** y **Environments: read/write**. El script prepara
`demo-apk-release` para la rama `main` y pide revisar antes de escribir en GitHub.
Usa por defecto el alias `demo-common` y un nombre de archivo del almacén de
claves específico del repositorio dentro de la carpeta de secretos del proyecto.
Mantén el almacén de claves fuera de la copia de trabajo y guarda una copia de
seguridad segura.

Introduce contraseñas distintas para el almacén y la clave, o pulsa Intro en
cualquiera de las preguntas para generar una contraseña de 25 caracteres. Guarda
las contraseñas generadas en un gestor de contraseñas cuando se te indique.
Solo se muestran si lo autorizas, por lo que debes usar una terminal sin
grabación de sesión. Se conservan los secretos de firma existentes. Si una
subida se interrumpe, vuelve a ejecutar con el almacén de claves, alias y
contraseñas originales.

Esta configuración prepara el entorno de firma. Compilar y adjuntar un APK
firmado a una publicación de GitHub corresponde a otro flujo de trabajo.

El asistente permite un proceso local por repositorio para evitar actualizaciones
simultáneas de la bóveda. Esto no coordina dispositivos distintos: configura el
entorno remoto desde un solo dispositivo a la vez. Se vuelven a comprobar las
reglas de despliegue exclusivo desde `main` de los entornos completados. Los
fallos inesperados de configuración usan un mensaje genérico para evitar
imprimir trazas que contengan credenciales.

Comprobaciones de regresión sin credenciales:
```sh
android-repo-setup workflows --check
```

## Configuración local

La configuración del repositorio se encuentra en `.project/setup/`:

- `config.yaml`: identidad del proyecto y versión de las herramientas compartidas.
- `repositories.yml`: destinos de publicación.
- `repositories.properties`: valores de publicación generados para Gradle.
- `workflow-generation.json`: hashes de los flujos generados (creado por la configuración).

Incluye estos archivos y los archivos generados de `.github/workflows/` en el
commit. Se ignora el bloqueo temporal `workflow-generation.lock`. Las claves de
firma y la bóveda cifrada permanecen fuera de la copia de trabajo, en
`~/.projects/<project>/secrets/`.

## Sitio de documentación

El sitio usa Zola 0.23.6 y la CLI Rust fijada; no requiere Python ni Node.js.
Instala ambas herramientas en `PATH` y ejecuta
`android-repo-docs build --check` desde la raíz del repositorio. El motor
opcional se configura en `sites/zola.toml`; la
[guía del sitio](../sites/README.md) explica la responsabilidad sobre el contenido,
las páginas en inglés y español por versión, los hashes de traducción revisados,
la vista previa local y el despliegue en Pages. Los metadatos de versiones
confirmadas siguen siendo la fuente de referencia; compilar la documentación
nunca publica artefactos Android ni cambia las identidades históricas del código
fuente.
