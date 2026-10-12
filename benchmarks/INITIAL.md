# Medición inicial — 11 de octubre de 2026

Dataset completo: 140.256 filas, columnas `hs`, `tp`, `dir`, inicio en el
índice 27359 (máximo de `tp`). Cinco repeticiones por carga, límite de 30 s.
Todas terminaron. Tiempo medio del comando completo, en segundos:

| Selecciones | v0.1.0 | v0.1.1 | Referencia de entonces |
| --- | ---: | ---: | ---: |
| 2 | 2,107 | 2,039 | 2,038 |
| 3 | 3,769 | 3,923 | 3,771 |
| 5 | 7,662 | 7,495 | 7,528 |

Las tres variantes coincidieron en índices y orden. Con cinco selecciones:
`[27359, 128807, 123587, 55022, 123571]`. También coincidieron en los
sintéticos (1.000 filas, semilla 42) y pasaron los seis casos pequeños.
El máximo RSS de la referencia con cinco selecciones fue 207,6 MiB,
incluidos datos e imports. Estas diferencias de tiempo no demuestran mejoras.

Entorno: Python 3.12.3, NumPy 1.26.0, SciPy 1.15.1, Hyperfine 1.18.0;
Linux WSL2 aarch64, 12 CPU lógicas. Tiempos dependientes de la máquina.
SHA-256 de `datawave.npz`:
`f90a405168601acaff280b46997280180eb03b91e72c4cf60450bb533daae354`.

La tabla conserva los nombres y mediciones originales. La referencia de
entonces era una copia del núcleo actual, con entrada convertida a `float32`.
Ahora solo se comparan el histórico `v0.1.1` y la API del checkout.
Los datos originales, incluido `initial-summary.json`, se archivaron en
`results/initial/`, conservados localmente e ignorados por Git. Las etiquetas
permiten recuperar los algoritmos originales.

## Tras corregir el orden de conversión — 12 de octubre de 2026

Las desviaciones de la API actual se calculan con el tipo original de entrada;
la matriz y salida siguen siendo `float32`. Metadatos del proyecto: `0.1.1`.
Se repitieron las mismas cargas, con cinco repeticiones y límite de 30 s:

| Selecciones | v0.1.1 histórico (s) | API corregida (s) |
| --- | ---: | ---: |
| 2 | 2,016 | 1,797 |
| 3 | 3,595 | 3,337 |
| 5 | 6,914 | 6,286 |

Todas las cargas terminaron y coincidieron exactamente en índices y orden,
incluidos los cinco índices de la tabla inicial. También coinciden los
sintéticos y los ocho casos pequeños, incluidos los dos del fix. El máximo
RSS de la API actual con cinco selecciones fue 202,7 MiB.
Los datos están en `results/fix-original-deviation/`.

No se declara una mejora de rendimiento: el histórico imprime progreso,
la API actual es silenciosa y los tiempos varían entre ejecuciones.
