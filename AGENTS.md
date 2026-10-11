# AGENTS.md

## Proyecto

`mdapy` selecciona observaciones mediante el algoritmo de máxima disimilitud.
Es una biblioteca educativa que también debe resultar cómoda de instalar y usar.
La evolución del algoritmo debe poder explicarse y medirse con ejemplos.

## Forma de trabajar

- Antes de modificar archivos, explica el cambio previsto y espera la aprobación
  del usuario.
- La aprobación para modificar no autoriza a hacer commit ni push; pide permiso
  explícito para cada operación.
- Mantén separadas las subfases de API, corrección, rendimiento y publicación.
  No introduzcas optimizaciones mientras se esté revisando el contrato de uso.
- Al cambiar el algoritmo, fija primero los casos de referencia y las reglas
  numéricas: entrada, salida, orden de selección, desempates y tolerancias.
  Compara los índices seleccionados antes de afirmar que una versión equivale a otra.
- Para medir rendimiento, registra tamaño y tipo de datos, semilla, número de
  selecciones, entorno, tiempo de preparación y tiempo de ejecución. Conserva
  una referencia ejecutable para comparar versiones, sin exponer implementaciones
  históricas como API principal por accidente.
- Respeta los cambios existentes aunque el árbol de trabajo no esté limpio.
  No borres prototipos, notebooks ni otros archivos del usuario sin explicar
  primero por qué deben salir del árbol activo.
- Mantén los cambios pequeños y centrados en la petición. Señala cualquier
  cambio adicional que parezca necesario antes de incluirlo en la subfase.
- Explica los resultados y las limitaciones en español, con ejemplos concretos
  cuando cambie el comportamiento visible.

## Git

- Todas las pull requests se integran mediante merge commit. No uses squash ni rebase.
- `main` contiene la versión estable y demostrable; `develop` integra los siguientes cambios.
- Las ramas de trabajo parten normalmente de `develop`. Los hotfix parten de `main` y sus cambios deben incorporarse después a `develop`.
- El merge commit debe mantener el título estándar `Merge pull request #...` y tener el cuerpo vacío. No repitas un título `feat:` o `fix:` en su cuerpo: Release Please lo contabilizaría además de los commits originales y duplicaría el changelog.
- Al fusionar una rama temporal, elimina la rama remota con `gh pr merge NUMERO --merge --delete-branch --subject "Merge pull request #NUMERO from propietario/rama" --body ""`.
- Tras verificar la fusión, actualiza la rama de destino y elimina la rama local temporal con `git branch -d RAMA`. No uses `git branch -D` sin autorización explícita.
- Ejecuta `git fetch --prune` para retirar referencias remotas obsoletas.
- No elimines nunca las ramas permanentes `main` o `develop`; no uses `--delete-branch` cuando cualquiera de ellas sea la rama origen de la pull request.

## Comprobaciones

- Usa `uv run` para ejecutar Python en el entorno del proyecto.
- Tras cambios, ejecuta `make format`, `make lint` y `make test`.
- Tras modificar un workflow de GitHub Actions, si `act` está instalado, ejecuta localmente el workflow afectado y comprueba que finaliza correctamente.
- Para cambios de ejemplos, ejecuta una comprobación específica del ejemplo,
  además de las pruebas pertinentes.
- Si una comprobación no puede ejecutarse, explica cuál faltó y por qué. No
  presentes como terminada una subfase cuyas pruebas relevantes fallen.

## Dependencias

- No añadas dependencias de producción sin consultarlo.
- Las dependencias directas nuevas o modificadas, incluidas las de desarrollo,
  deben declarar un límite superior anterior a la siguiente versión mayor.
  Si hace falta una excepción, acuerda y documenta el motivo. Las restricciones
  existentes no se cambian fuera de una subfase de dependencias acordada.
- Cuando cambies dependencias, actualiza también `uv.lock` y comprueba que
  sigue correspondiendo a `pyproject.toml`.
