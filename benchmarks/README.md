# Benchmarks

```bash
uv run benchmarks/run.py
```

Requiere Hyperfine y GNU `timeout`. Ejecuta todos los `.py` de `algorithms/`:
`current.py` adapta la API pública del checkout; los demás conservan
una copia por versión menor, con su último fix (`v0_n_max.py`). Cada archivo
expone `max_diss_alg(data_tuple, n_clusters, seed_index, dir_indices)` y devuelve
las filas seleccionadas y sus índices en orden.

Primero comprueba `cases.json`. Después mide todo `datawave.npz`, con
2, 3 y 5 selecciones, cinco repeticiones y procesos independientes. El límite
es de 30 segundos por ejecución; un fallo detiene la progresión. Para acortar:

```bash
uv run benchmarks/run.py --counts 2 --timeout 15
```

El ejecutor guarda los datos en `results/`, ignorado por Git: tiempos de
Hyperfine, índices, memoria y entorno. Después interpretamos los resultados
y redactamos manualmente `RESULTS.md`.

El tiempo de llamada mide `max_diss_alg` completo: construcción de la matriz,
cálculo de desviaciones y selección. Hyperfine mide además arranque, imports,
carga de datos y escritura. El RSS máximo incluye imports y datos.

`preparation_s` mide la carga del módulo, no la preparación de la matriz.
La llamada de `current.py` incluye construir los `DataColumn`. La referencia
histórica sigue formateando y escribiendo el progreso a `/dev/null`; la API
actual es silenciosa. La comparación mide estas llamadas completas y no
permite atribuir toda la diferencia de tiempo al núcleo numérico.
Las mediciones anteriores se conservan con su alcance original.
