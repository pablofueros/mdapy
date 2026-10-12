# Comparación de MDA

Desde la raíz del proyecto, con Hyperfine y GNU `timeout` instalados:

```bash
uv run python benchmarks/run.py suite
```

Compara el algoritmo histórico `v0.1.1` con la API actual del checkout.
`history/versions.json` indica qué archivo cargar, qué API usar y su procedencia.
`cases.json` contiene ejemplos con índices esperados, incluidos los del fix
que calcula las desviaciones antes de convertir la matriz a `float32`.
Ruff puede formatear el núcleo histórico; su original está en la etiqueta Git.

Las cargas son datos sintéticos de 1.000 filas (semilla 42) y todo
`datawave.npz` (140.256 filas, `hs`, `tp`, `dir`, inicio en el máximo de `tp`).
Se prueban 2, 3 y 5 selecciones, con cinco repeticiones y procesos independientes.
Una exploración previa y un límite de 30 segundos evitan aumentar la carga
si una versión falla o tarda demasiado. Se exige igualdad exacta de índices
y orden antes y después de medir.

Para una comprobación más corta:

```bash
uv run python benchmarks/run.py suite --counts 2 --timeout 15
```

Cada ejecución crea una carpeta en `results/`, ignorada por Git. Hyperfine
guarda el tiempo del comando completo; los JSON `run-*` guardan índices,
entorno, tipos, hash del dataset, memoria máxima y tiempos internos. También
puedes elegir una carpeta vacía con `--output`.

La preparación mide la carga del módulo y, en la API actual, la construcción
de `DataColumn`. La llamada al algoritmo incluye su preparación interna.
El RSS incluye datos e imports; el tiempo de Hyperfine incluye además el
arranque y la escritura del informe. El histórico sigue generando progreso,
redirigido a `/dev/null`; la API actual es silenciosa.

No se cambia la precisión del algoritmo. Coincidir en estas cargas no prueba
equivalencia para cualquier entrada. `INITIAL.md` conserva la medición inicial.
Se guarda un núcleo por evolución significativa, usando su último parche;
los fixes requieren regresiones, según `AGENTS.md`.
