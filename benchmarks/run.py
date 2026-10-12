"""Compare the historical algorithm and current API in bounded processes."""

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
VERSIONS = json.loads((ROOT / "history/versions.json").read_text())


def select(version, arrays, directional, count, seed):
    begin = perf_counter()
    if VERSIONS[version]["api"] == "columns":
        from mdapy import DataColumn, max_diss_alg

        columns = [
            DataColumn(a, directional=i in directional) for i, a in enumerate(arrays)
        ]
        preparation = perf_counter() - begin
        begin = perf_counter()
        points, indices = max_diss_alg(*columns, n_clusters=count, seed_index=seed)
    else:
        spec = importlib.util.spec_from_file_location(
            "historical", ROOT / "history" / VERSIONS[version]["file"]
        )
        assert spec is not None and spec.loader is not None
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        preparation = perf_counter() - begin
        begin = perf_counter()
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
            points, indices = engine.max_diss_alg(arrays, count, seed, directional)
    return points, indices, preparation, perf_counter() - begin


def check(version):
    cases = json.loads((ROOT / "cases.json").read_text())
    for case in cases:
        arrays = tuple(np.asarray(a, dtype=float) for a in case["columns"])
        points, indices, _, _ = select(
            version,
            arrays,
            case["directional"],
            len(case["expected"]),
            case["seed_index"],
        )
        if indices != case["expected"]:
            raise ValueError(f"Unexpected indices: {version}, {case['name']}")
        np.testing.assert_array_equal(
            points, np.array(arrays, dtype=points.dtype).T[indices]
        )
    print(f"{version}: {len(cases)} reference cases passed", flush=True)


def provenance(version):
    source = dict(VERSIONS[version])
    if source["api"] == "tuple":
        paths = [ROOT / "history" / source["file"]]
    else:
        import mdapy

        paths = sorted(Path(mdapy.__file__).resolve().parent.glob("*.py"))
        source["revision"] = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        source["modified"] = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--", "src/mdapy"],
                cwd=ROOT.parent,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return source, digest.hexdigest()


def worker(args):
    begin = perf_counter()
    if args.dataset == "wave":
        path = ROOT.parent / "examples/data/datawave.npz"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with np.load(path) as data:
            arrays = tuple(data[key] for key in ("hs", "tp", "dir"))
        directional, seed = [2], int(np.argmax(arrays[1]))
    else:
        digest = None
        rng = np.random.default_rng(args.seed)
        arrays = (rng.normal(size=args.rows), rng.uniform(0, 360, args.rows))
        directional, seed = [1], 0
    load_s = perf_counter() - begin
    if not 1 <= args.selections <= len(arrays[0]):
        raise ValueError("selections must be between 1 and the number of rows")
    points, indices, prep_s, call_s = select(
        args.version, arrays, directional, args.selections, seed
    )
    total_s = perf_counter() - begin
    source, source_hash = provenance(args.version)
    record = {
        "version": args.version,
        "source": source,
        "source_sha256": source_hash,
        "dataset": args.dataset,
        "dataset_sha256": digest,
        "rows": len(arrays[0]),
        "columns": len(arrays),
        "original_dtype": [str(a.dtype) for a in arrays],
        "output_dtype": str(points.dtype),
        "matrix_dtype": "float32" if source["api"] == "tuple" else None,
        "random_seed": args.seed if args.dataset == "synthetic" else None,
        "seed_index": seed,
        "selections": args.selections,
        "indices": indices,
        "sampling": "all rows in original order",
        "load_s": load_s,
        "preparation_s": prep_s,
        "algorithm_call_s": call_s,
        "total_s": total_s,
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        * (1 if sys.platform == "darwin" else 1024),
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "threads": {
                key: os.environ.get(key)
                for key in (
                    "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS",
                )
            },
        },
    }
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / f"run-{uuid.uuid4().hex}.json").write_text(json.dumps(record, indent=2))


def verify(output, dataset, count):
    records = [json.loads(p.read_text()) for p in output.glob("run-*.json")]
    indices = [
        r["indices"]
        for r in records
        if r["dataset"] == dataset and r["selections"] == count
    ]
    if not indices or any(value != indices[0] for value in indices):
        raise ValueError(f"Selection discrepancy: {dataset}, K={count}")


def suite(args):
    if not all(shutil.which(tool) for tool in ("hyperfine", "timeout")):
        raise RuntimeError("Install Hyperfine and GNU timeout")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use an empty output directory for each measurement")
    script = [sys.executable, str(Path(__file__).resolve())]
    for version in VERSIONS:
        subprocess.run(
            [*script, "check", "--version", version], check=True, timeout=args.timeout
        )
    statuses = []
    for dataset in ("synthetic", "wave"):
        for count in args.counts:
            commands = []
            try:
                for version in VERSIONS:
                    cmd = [
                        *script,
                        "worker",
                        "--version",
                        version,
                        "--dataset",
                        dataset,
                        "--selections",
                        str(count),
                        "--rows",
                        str(args.rows),
                        "--seed",
                        str(args.seed),
                        "--output",
                        str(output),
                    ]
                    subprocess.run(cmd, check=True, timeout=args.timeout)
                    commands.append(
                        shlex.join(
                            ["timeout", "--signal=KILL", f"{args.timeout}s", *cmd]
                        )
                    )
                verify(output, dataset, count)
                subprocess.run(
                    [
                        "hyperfine",
                        "--shell=none",
                        "--runs",
                        str(args.runs),
                        "--export-json",
                        str(output / f"hyperfine-{dataset}-k{count}.json"),
                        *commands,
                    ],
                    check=True,
                )
                verify(output, dataset, count)
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
                statuses.append(
                    {
                        "dataset": dataset,
                        "selections": count,
                        "status": type(exc).__name__,
                    }
                )
                print(
                    f"Stopping {dataset} at K={count}: {type(exc).__name__}", flush=True
                )
                break
            statuses.append({"dataset": dataset, "selections": count, "status": "ok"})
    (output / "status.json").write_text(json.dumps(statuses, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "worker", "suite"))
    parser.add_argument("--version", choices=VERSIONS, default="candidate")
    parser.add_argument("--dataset", choices=("synthetic", "wave"), default="wave")
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--selections", type=int, default=2)
    parser.add_argument("--counts", type=int, nargs="+", default=[2, 3, 5])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", default=str(ROOT / "results" / uuid.uuid4().hex))
    args = parser.parse_args()
    if args.timeout <= 0 or args.rows < 2 or args.runs < 2:
        parser.error("timeout > 0, rows >= 2 and runs >= 2 are required")
    if args.selections < 1 or not args.counts or min(args.counts) < 1:
        parser.error("selection counts must be positive")
    if args.counts != sorted(set(args.counts)):
        parser.error("counts must be strictly increasing")
    if args.mode == "check":
        check(args.version)
    elif args.mode == "worker":
        worker(args)
    else:
        suite(args)


if __name__ == "__main__":
    main()
