"""Benchmark every algorithm in algorithms/ with Hyperfine."""

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import platform
import resource
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "examples/data/datawave.npz"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.max_diss_alg


def worker(args, path):
    begin = perf_counter()
    algorithm = load(path)
    preparation = perf_counter() - begin
    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        if args.check:
            for case in json.loads((ROOT / "cases.json").read_text()):
                arrays = tuple(np.asarray(a, dtype=float) for a in case["columns"])
                points, indices = algorithm(
                    arrays,
                    len(case["expected"]),
                    case["seed_index"],
                    case["directional"],
                )
                if indices != case["expected"]:
                    raise ValueError(f"Unexpected indices: {path.stem}, {case['name']}")
                np.testing.assert_array_equal(
                    points, np.array(arrays, dtype=points.dtype).T[indices]
                )
            return
        begin = perf_counter()
        with np.load(DATA) as data:
            arrays = tuple(data[key] for key in ("hs", "tp", "dir"))
        seed = int(np.argmax(arrays[1]))
        load_s = perf_counter() - begin
        if not 1 <= args.selections <= len(arrays[0]):
            raise ValueError("Invalid selection count")
        begin = perf_counter()
        points, indices = algorithm(arrays, args.selections, seed, [2])
        elapsed = perf_counter() - begin
    record = {
        "probe": args.probe,
        "rows": len(arrays[0]),
        "columns": 3,
        "input_dtype": [str(a.dtype) for a in arrays],
        "output_dtype": str(points.dtype),
        "seed_index": seed,
        "sampling": "all rows in original order",
        "selections": args.selections,
        "indices": indices,
        "load_s": load_s,
        "preparation_s": preparation,
        "algorithm_s": elapsed,
        "peak_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        / (2**20 if sys.platform == "darwin" else 1024),
    }
    with (Path(args.output) / f"{path.stem}-k{args.selections}.jsonl").open("a") as f:
        f.write(json.dumps(record) + "\n")


def benchmark(args, algorithms):
    if not all(shutil.which(tool) for tool in ("hyperfine", "timeout")):
        raise RuntimeError("Install Hyperfine and GNU timeout")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Choose an empty output directory")
    script = [sys.executable, str(Path(__file__).resolve())]
    for path in algorithms:
        subprocess.run(
            [*script, "--algorithm", path.stem, "--check"],
            check=True,
            timeout=args.timeout,
        )
    metadata = {
        "python": platform.python_version(), "numpy": np.__version__,
        "scipy": scipy.__version__, "platform": platform.platform(),
        "cpu_count": os.cpu_count(), "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "algorithms": [path.name for path in algorithms], "counts": args.counts,
        "runs": args.runs, "timeout_s": args.timeout,
        "hyperfine": subprocess.run(["hyperfine", "--version"], check=True,
                                    capture_output=True, text=True).stdout.strip(),
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2))
    for count in args.counts:
        expected = None
        for path in algorithms:
            command = [
                *script,
                "--algorithm",
                path.stem,
                "--selections",
                str(count),
                "--output",
                str(output),
            ]
            export = output / f"{path.stem}-k{count}-hyperfine.json"
            try:
                subprocess.run([*command, "--probe"], check=True, timeout=args.timeout)
                subprocess.run(
                    [
                        "hyperfine",
                        "--shell=none",
                        "--runs",
                        str(args.runs),
                        "--export-json",
                        str(export),
                        shlex.join(
                            ["timeout", "--signal=KILL", f"{args.timeout}s", *command]
                        ),
                    ],
                    check=True,
                )
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
                raise RuntimeError(
                    f"Stopped at {path.stem}, K={count}; no larger loads"
                ) from exc
            records = [
                json.loads(line)
                for line in (output / f"{path.stem}-k{count}.jsonl")
                .read_text()
                .splitlines()
            ]
            if expected is None:
                expected = records[0]["indices"]
            if any(r["indices"] != expected for r in records):
                raise ValueError(f"Selection discrepancy: {path.stem}, K={count}")
    print(f"Datos guardados en {output}. Redacta el informe después de interpretarlos.")


def main():
    algorithms = sorted((ROOT / "algorithms").glob("*.py"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--counts", nargs="+", type=int, default=[2, 3, 5])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", default=str(ROOT / "results" / uuid.uuid4().hex))
    parser.add_argument(
        "--algorithm", choices=[p.stem for p in algorithms], help=argparse.SUPPRESS
    )
    parser.add_argument("--selections", type=int, default=2, help=argparse.SUPPRESS)
    parser.add_argument("--check", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--probe", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not algorithms or args.timeout <= 0 or args.runs < 2:
        parser.error(
            "Algorithms, a positive timeout and at least two runs are required"
        )
    if min(args.counts) < 1 or args.counts != sorted(set(args.counts)):
        parser.error("counts must be positive and strictly increasing")
    if args.algorithm:
        worker(args, ROOT / "algorithms" / f"{args.algorithm}.py")
    else:
        benchmark(args, algorithms)


if __name__ == "__main__":
    main()
