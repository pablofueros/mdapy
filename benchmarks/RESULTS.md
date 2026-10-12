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
