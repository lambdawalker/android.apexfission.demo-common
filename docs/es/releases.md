# Publicación de Demo Common

Solo se publica el AAR `release` de `:demo-common`. Gradle se ejecuta en JDK 21
y produce bytecode compatible con Java 17.

## Configuración inicial

Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) y ejecuta
`uv run scripts/setup.py setup_github_environments`. Usa un token de GitHub limitado
a este repositorio con los permisos de administración de entornos indicados por
el asistente. Revisa los cambios antes de aplicarlos. Maven Central requiere
`MAVEN_CENTRAL_USERNAME`, `MAVEN_CENTRAL_PASSWORD`, `SIGNING_IN_MEMORY_KEY`
y la contraseña de firma si corresponde. Introduce la ruta al archivo de la
clave de firma exportada. Confirma la propiedad del espacio de nombres en
Central Portal. JitPack público usa un entorno vacío y requiere un repositorio
público en GitHub.

Configura un temporizador de espera de 15 minutos en `delayed-docs` cuando esté
disponible. En Settings → Pages, selecciona GitHub Actions.

## Publicar

Ejecuta **Publish Demo Common** en `main`. Elige Maven Central o JitPack y deja
**version** en blanco. La primera versión es `0.1.0`. Si las entradas de la
publicación no cambian, se reutilizan la última versión y revisión inmutables.
Si cambian, se incrementa el parche.

## Recuperación

Conserva las etiquetas canónicas, `release-pending` y `release-uploading` si se
interrumpe una ejecución. Inspecciona el registro de publicación y el estado del
proveedor. Ejecuta **Finalize Demo Common release** con el mismo destino y la
versión reservada para verificar y finalizar sin volver a subir artefactos.

Si un intento en Maven Central nunca llegó a publicarse y Central Portal
confirma que no existe despliegue, archiva las etiquetas `release-pending` y
`release-uploading` en `release-failed/` mediante
`uv run scripts/setup.py module_release abort-unconfirmed --module demo-common --version X.Y.Z`
(que comprueba `published_versions` en Maven Central antes de archivar).

## Verificar sin publicar

```sh
uv run scripts/setup.py publishing_config check
uv run scripts/setup.py import_docs --check
uv run scripts/setup.py build_docs --check
uv run scripts/setup.py workflows --check
./gradlew verifyImportDocs :demo-common:testDebugUnitTest :demo-common:lintRelease :demo-common:assembleRelease
```

## Preparar la firma de un APK de demostración

Ejecuta `./setup.sh` en Linux o macOS, o `setup.bat` en Windows desde una
terminal privada con JDK y uv. Ambos lanzadores usan la versión
`v0.1.4` del asistente compartido
[Android Repository Setup](https://github.com/lambdawalker/python.android-repo-setup)
y abren la bóveda cifrada local en `~/.projects/android.apexfission.demo-common/secrets/`.

Comprobaciones de regresión sin credenciales:
```sh
uv run scripts/setup.py workflows --check
```

## Configuración local

La configuración se guarda en `.project/setup/`: `config.yaml` identifica el
proyecto y la versión de las herramientas; `repositories.yml` define los destinos;
`repositories.properties` contiene los valores generados para Gradle y
`workflow-generation.json` registra los hashes de los workflows generados.
Incluye estos archivos y `.github/workflows/` en el commit. El bloqueo temporal
se ignora. Las claves y la bóveda permanecen fuera del repositorio en
`~/.projects/<project>/secrets/`.
