# Benchmarks

```bash
uv run benchmarks/run.py
```

Requiere Hyperfine y GNU `timeout`. Ejecuta todos los `.py` de `algorithms/`:
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
