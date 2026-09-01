#!/usr/bin/env python3
"""Paired CPU benchmark runner for native BioNetGen workloads.

Each executable invocation runs in a fresh directory and child process. Pairs
alternate which executable runs first so scheduler and thermal drift are not
confounded with the candidate. The JSON output is intentionally raw enough to
support independent statistical summaries.
"""

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

try:
    import resource
except ImportError:  # pragma: no cover - Windows has no resource module
    resource = None


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def output_files(run_dir, model_name):
    return sorted(
        path for path in pathlib.Path(run_dir).iterdir()
        if path.name != model_name and path.is_file()
    )


def net_counts(path):
    counts = {"species_count": None, "reaction_count": None}
    if not path.exists():
        return counts

    section = None
    for raw_line in path.read_text(errors="replace").splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if lower.startswith("begin "):
            section = lower[6:].strip()
            continue
        if lower == "end" or lower.startswith("end "):
            section = None
            continue
        if section == "species" and line and not line.startswith("#"):
            counts["species_count"] = (counts["species_count"] or 0) + 1
        elif section in ("reactions", "reaction rules") and line and not line.startswith("#"):
            counts["reaction_count"] = (counts["reaction_count"] or 0) + 1
    return counts


def data_row_count(path):
    if not path.exists():
        return 0
    return sum(
        1 for raw_line in path.read_text(errors="replace").splitlines()
        if raw_line.strip() and not raw_line.lstrip().startswith("#")
    )


def run_worker(args):
    run_dir = pathlib.Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    model_name = pathlib.Path(args.model).name
    model_path = run_dir / model_name
    shutil.copy2(args.model, model_path)

    before = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [args.executable, str(model_path)],
            cwd=run_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=args.timeout,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + "\nbenchmark timeout\n"

    elapsed = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN) if resource else None
    files = output_files(run_dir, model_name)
    net_path = run_dir / (pathlib.Path(model_name).stem + ".net")
    hashes = {path.name: sha256(path) for path in files}
    sizes = {path.name: path.stat().st_size for path in files}
    counts = net_counts(net_path)
    counts["output_row_count"] = sum(
        data_row_count(path) for path in files if path.suffix in (".gdat", ".cdat")
    ) or None

    result = {
        "returncode": returncode,
        "wall_seconds": elapsed,
        "cpu_user_seconds": (after.ru_utime - before.ru_utime) if resource else None,
        "cpu_system_seconds": (after.ru_stime - before.ru_stime) if resource else None,
        "max_rss": after.ru_maxrss if resource else None,
        "output_sizes": sizes,
        "output_hashes": hashes,
        "output_bytes": sum(sizes.values()),
        "counts": counts,
        "stdout": stdout,
        "stderr": stderr,
        "command": [args.executable, str(model_path)],
    }
    print(json.dumps(result), flush=True)
    return returncode


def run_one(script, executable, model, run_dir, timeout):
    completed = subprocess.run(
        [sys.executable, script, "--worker", "--executable", executable,
         "--model", model, "--run-dir", str(run_dir), "--timeout", str(timeout)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if not completed.stdout.strip():
        raise RuntimeError("worker failed: " + completed.stderr)
    return json.loads(completed.stdout.strip().splitlines()[-1])


def run_matrix(args):
    executable_a = os.path.abspath(args.executable_a)
    executable_b = os.path.abspath(args.executable_b)
    models = [os.path.abspath(model) for model in args.models]
    results = []

    with tempfile.TemporaryDirectory(prefix="bng-paired-") as root:
        root_path = pathlib.Path(root)
        pair_index = 0
        for model in models:
            for repetition in range(1, args.repetitions + 1):
                first_a = (pair_index % 2) == 0
                order = [("baseline", executable_a), ("candidate", executable_b)]
                if not first_a:
                    order.reverse()

                pair = {}
                for label, executable in order:
                    run_dir = root_path / pathlib.Path(model).stem / str(repetition) / label
                    data = run_one(args.script, executable, model, run_dir, args.timeout)
                    data.update({
                        "label": label,
                        "model": model,
                        "model_sha256": sha256(model),
                        "repetition": repetition,
                        "pair_index": pair_index,
                    })
                    pair[label] = data
                    results.append(data)

                if pair["baseline"]["returncode"] != 0 or pair["candidate"]["returncode"] != 0:
                    raise RuntimeError(json.dumps(pair, indent=2))
                pair_index += 1

    payload = {
        "executable_a": executable_a,
        "executable_b": executable_b,
        "executable_a_sha256": sha256(executable_a),
        "executable_b_sha256": sha256(executable_b),
        "repetitions": args.repetitions,
        "timeout_seconds": args.timeout,
        "results": results,
    }
    pathlib.Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": args.output, "records": len(results)}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--executable")
    parser.add_argument("--model", action="append", dest="models")
    parser.add_argument("--executable-a")
    parser.add_argument("--executable-b")
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", default="portable_cpu_benchmark.json")
    parser.add_argument("--run-dir")
    parser.add_argument("--script", default=os.path.abspath(__file__))
    args = parser.parse_args()

    if args.worker:
        if not args.run_dir or not args.executable or not args.models:
            parser.error("worker mode requires --executable, --model, and --run-dir")
        args.model = args.models[0]
        return run_worker(args)

    if not args.executable_a or not args.executable_b or not args.models:
        parser.error("matrix mode requires --executable-a, --executable-b, and --model")
    run_matrix(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
