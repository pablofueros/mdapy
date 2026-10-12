# Resultados

## Entorno de ejecución

Medición realizada el **12 de octubre de 2026**, en Linux sobre WSL2,
con arquitectura ARM64 y 12 CPU lógicas.

Se utilizaron Python 3.12.3, NumPy 1.26.0, SciPy 1.15.1 y Hyperfine 1.18.0.
Los tiempos sirven como referencia para esta máquina.

## Punto de partida

Hemos medido `v0_1_2.py` sobre las **140.256 observaciones** de `datawave.npz`,
usando las variables `hs`, `tp` y `dir`. Se empieza por la observación con
mayor `tp` (índice 27359). Los datos de entrada son `float64`; la matriz de
trabajo y la salida son `float32`.

Para avanzar sin ejecuciones demasiado largas, probamos 2, 3 y 5 selecciones.
Cada carga se repitió cinco veces en procesos independientes, con un límite
de 30 segundos por ejecución. Todas terminaron dentro del límite.

| Selecciones | Tiempo total medio (s) | Algoritmo, mediana (s) | Memoria máxima (MiB) |
| ---: | ---: | ---: | ---: |
| 2 | 1,989 | 1,593 | 132,0 |
| 3 | 3,725 | 3,307 | 146,6 |
| 5 | 7,521 | 7,036 | 196,3 |

El tiempo total incluye arrancar Python, cargar los datos y guardar la medición.
El tiempo del algoritmo incluye preparar su matriz, calcular las desviaciones
y seleccionar las observaciones. La memoria corresponde al proceso completo.
El progreso por pantalla se redirigió a `/dev/null`.

## Qué nos dicen los resultados

Con dos selecciones la ejecución ronda los dos segundos; con cinco supera
los siete. La memoria también aumenta, de 132 a 196 MiB. Manteniendo todas
las observaciones, aumentar las selecciones ya tiene un coste apreciable.

Los ocho casos de referencia pasaron y todas las repeticiones eligieron los
mismos índices en el mismo orden. Esta medición será nuestra base para
comprobar si las próximas optimizaciones reducen tiempo y memoria conservando
las selecciones en los casos comparados.

Los datos detallados de esta ejecución están en `results/current/`.

## Subfase 2.1 — Mínimos incrementales y NumPy

Nueva medición del **12 de octubre de 2026**, en el mismo entorno, con las
mismas 140.256 filas, variables, tipos y semilla inicial. Se comparan la
referencia independiente `v0_1_2.py` y la API pública mediante `current.py`.
El checkout medido corresponde a los cambios sin commit de la rama
`perf/mda-optimization`, sobre `30818bb`. Los resultados del punto de partida
se conservan arriba; esta tabla corresponde a una ejecución nueva.

Se mantienen cinco repeticiones en procesos independientes y el límite de
30 segundos. Todas las ejecuciones terminaron y seleccionaron los mismos
índices en el mismo orden. Pasaron también los once casos de referencia,
incluidos los nuevos casos de casi empate, dos variables direccionales y
ángulos fuera de una vuelta.

| Selecciones | Referencia, llamada mediana (s) | Actual, llamada mediana (s) | Referencia, memoria máxima (MiB) | Actual, memoria máxima (MiB) |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1,666 | 0,186 | 133,3 | 112,0 |
| 3 | 3,415 | 0,383 | 148,3 | 109,8 |
| 5 | 6,698 | 0,773 | 200,4 | 118,3 |

Para cinco selecciones, el tiempo total medio del proceso pasó de 7,193 a
1,148 segundos. Ambas versiones eligieron
`[27359, 128807, 123587, 55022, 123571]`.

La implementación actual guarda una distancia mínima por candidato y solo
la actualiza frente al último punto elegido. Evita la caché de pares y los
recorridos del subconjunto; vectoriza diferencias y normalización y reutiliza
las desviaciones calculadas por la API. Conserva la norma por fila: reducir
por un eje o comparar cuadrados puede cambiar los empates en `float32`.

Son tiempos de llamadas completas: la actual incluye construir los
`DataColumn`, mientras la referencia sigue generando progreso a `/dev/null`.
La diferencia no mide exclusivamente la mejora del núcleo. La memoria es
el RSS máximo del proceso, incluidos imports y datos. La igualdad observada
corresponde a los casos y cargas comparados en este entorno.

Los datos detallados están en `results/numpy-incremental/`. Se reproducen con:

```bash
uv run benchmarks/run.py --output benchmarks/results/otra-ejecucion
```

## Cierre de Python/NumPy — Columnas protegidas

Medición del **13 de octubre de 2026** sobre el commit `256380c`, después de
separar el núcleo en `core.py`, retirar `DataMatrix` de producción y proteger
los datos de `DataColumn`. La llamada actual incluye las copias de entrada
necesarias para mantener coherente la desviación guardada.

Se repitió el protocolo anterior en el mismo entorno: todas las 140.256 filas,
entrada `float64`, matriz y salida `float32`, semilla 27359, 2/3/5 selecciones,
cinco repeticiones independientes y un límite de 30 segundos por ejecución.
Los once casos de referencia pasaron. Todas las ejecuciones terminaron y
conservaron los índices y su orden, tanto entre implementaciones como frente
a la medición anterior.

| Selecciones | Referencia, llamada mediana (s) | Actual, llamada mediana (s) | Referencia, memoria máxima (MiB) | Actual, memoria máxima (MiB) |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1,704 | 0,205 | 129,3 | 114,1 |
| 3 | 3,544 | 0,393 | 158,1 | 123,0 |
| 5 | 7,593 | 0,801 | 198,6 | 115,4 |

Respecto a la primera implementación optimizada, las medianas de la llamada
actual aumentaron un 10,0 %, 2,4 % y 3,6 %, respectivamente. El rendimiento
sigue en un rango similar con las columnas protegidas. El RSS máximo varía
entre procesos y no permite aislar por sí solo el coste de las nuevas copias.

Para cinco selecciones, el tiempo total medio fue de 8,112 segundos en la
referencia y 1,145 en la API actual. Los índices siguen siendo
`[27359, 128807, 123587, 55022, 123571]`.

Hyperfine señaló una primera ejecución actual más lenta con dos selecciones;
se conserva dentro de las cinco repeticiones, sin descartarla ni modificar
el protocolo. Se mantienen las limitaciones de alcance anteriores: llamadas
completas, progreso histórico a `/dev/null` y memoria del proceso completo.
Estos resultados cierran la comparación de Python/NumPy en las cargas medidas;
Numba queda para una rama y evaluación separadas.

Datos detallados en `results/python-final-2026-10-13/`. Comando utilizado:

```bash
uv run benchmarks/run.py --output benchmarks/results/python-final-2026-10-13
```
