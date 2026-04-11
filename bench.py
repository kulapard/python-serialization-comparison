"""
Benchmark: marshmallow vs marshmallow-recipe vs pydantic
========================================================
Compares dump (serialization) and load (deserialization) performance
across three popular Python serialization libraries.
All libraries operate on the same 10-level-deep dataclass hierarchy.
"""

from __future__ import annotations

import gc
import statistics
import time

import marshmallow_recipe as mr
import pydantic

from models import Organization, make_organization, make_organization_dict
from schemas import MaOrganizationSchema

OrgAdapter = pydantic.TypeAdapter(Organization)


# ──────────────────────────────────────────────
# 4. Benchmark harness
# ──────────────────────────────────────────────

def bench(fn, *, min_rounds: int = 10, budget: float = 10.0):
    """Return median execution time in seconds.

    Runs at least *min_rounds* iterations but stops after *budget* seconds
    of measurement to keep deep/large benchmarks practical.
    """
    gc.disable()
    try:
        times: list[float] = []
        deadline = time.perf_counter() + budget
        while len(times) < min_rounds or time.perf_counter() < deadline:
            t0 = time.perf_counter()
            fn()
            times.append(time.perf_counter() - t0)
            if len(times) >= 500:
                break
    finally:
        gc.enable()
    return statistics.median(times)


def fmt_time(seconds: float) -> str:
    us = seconds * 1_000_000
    if us < 1000:
        return f"{us:.1f} us"
    ms = us / 1000
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{seconds:.2f} s"


def speedup_str(base: float, other: float) -> str:
    if other == 0:
        return "-"
    ratio = base / other
    if ratio >= 1:
        return f"{ratio:.1f}x"
    return f"1/{1/ratio:.1f}x"


# ──────────────────────────────────────────────
# 5. Test data (generated once)
# ──────────────────────────────────────────────

SCALES = [1, 100, 1000]
_objs: dict[int, list] = {n: [make_organization() for _ in range(n)] for n in SCALES}
_dicts: dict[int, list[dict]] = {n: [make_organization_dict() for _ in range(n)] for n in SCALES}
_ma_schema = MaOrganizationSchema()


# ──────────────────────────────────────────────
# 6. Runners
# ──────────────────────────────────────────────

def run_dump_marshmallow(n: int):
    objs = _objs[n]
    return bench(lambda: [_ma_schema.dump(o) for o in objs])


def run_load_marshmallow(n: int):
    dicts = _dicts[n]
    return bench(lambda: [_ma_schema.load(d) for d in dicts])


def run_dump_mr(n: int):
    objs = _objs[n]
    return bench(lambda: [mr.dump(o) for o in objs])


def run_load_mr(n: int):
    dicts = _dicts[n]
    return bench(lambda: [mr.load(Organization, d) for d in dicts])


def run_dump_mr_nuked(n: int):
    objs = _objs[n]
    return bench(lambda: [mr.nuked.dump(Organization, o) for o in objs])


def run_load_mr_nuked(n: int):
    dicts = _dicts[n]
    return bench(lambda: [mr.nuked.load(Organization, d) for d in dicts])


def run_dump_pydantic(n: int):
    objs = _objs[n]
    return bench(lambda: [OrgAdapter.dump_python(o) for o in objs])


def run_load_pydantic(n: int):
    dicts = _dicts[n]
    return bench(lambda: [OrgAdapter.validate_python(d) for d in dicts])


# ──────────────────────────────────────────────
# 6. Table renderer
# ──────────────────────────────────────────────

def render_table(rows: list[list[str]], headers: list[str]) -> str:
    """Render a Unicode box-drawing table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def pad(cells):
        return [f" {c:<{widths[i]}} " for i, c in enumerate(cells)]

    top = "\u250c" + "\u252c".join("\u2500" * (w + 2) for w in widths) + "\u2510"
    mid = "\u251c" + "\u253c".join("\u2500" * (w + 2) for w in widths) + "\u2524"
    bot = "\u2514" + "\u2534".join("\u2500" * (w + 2) for w in widths) + "\u2518"
    header = "\u2502" + "\u2502".join(pad(headers)) + "\u2502"

    lines = [top, header, mid]
    for i, row in enumerate(rows):
        lines.append("\u2502" + "\u2502".join(pad(row)) + "\u2502")
        if i < len(rows) - 1:
            lines.append(mid)
    lines.append(bot)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 7. Main
# ──────────────────────────────────────────────

def main():
    import importlib.metadata

    scales = SCALES
    operations = ["dump", "load"]

    lib_runners = {
        "marshmallow": {"dump": run_dump_marshmallow, "load": run_load_marshmallow},
        "mr-recipe": {"dump": run_dump_mr, "load": run_load_mr},
        "mr-recipe-nuked": {"dump": run_dump_mr_nuked, "load": run_load_mr_nuked},
        "pydantic": {"dump": run_dump_pydantic, "load": run_load_pydantic},
    }
    lib_names = list(lib_runners.keys())

    # Print versions
    ma_ver = importlib.metadata.version("marshmallow")
    mr_ver = importlib.metadata.version("marshmallow-recipe")
    pyd_ver = importlib.metadata.version("pydantic")
    print()
    print(f"  marshmallow        {ma_ver}")
    print(f"  marshmallow-recipe {mr_ver}")
    print(f"  pydantic           {pyd_ver}")
    print()

    # Collect results: results[op][n][lib] = seconds
    results: dict[str, dict[int, dict[str, float]]] = {}
    total = len(operations) * len(scales) * len(lib_names)
    done = 0

    for op in operations:
        results[op] = {}
        for n in scales:
            results[op][n] = {}
            for lib in lib_names:
                done += 1
                tag = f"{op} x {n:<4} [{lib}]"
                print(f"  [{done:>2}/{total}] {tag:40s} ...", end="", flush=True)
                t = lib_runners[lib][op](n)
                results[op][n][lib] = t
                print(f" {fmt_time(t)}")

    # ── Pairwise comparison tables ──
    comparisons = [
        ("marshmallow", "mr-recipe"),
        ("marshmallow", "mr-recipe-nuked"),
        ("marshmallow", "pydantic"),
        ("mr-recipe", "mr-recipe-nuked"),
    ]

    for base_lib, cmp_lib in comparisons:
        headers = ["Operation", base_lib, cmp_lib, "Speedup"]
        rows = []
        for op in operations:
            for n in scales:
                t_base = results[op][n][base_lib]
                t_cmp = results[op][n][cmp_lib]
                rows.append([
                    f"{op} x {n}",
                    fmt_time(t_base),
                    fmt_time(t_cmp),
                    speedup_str(t_base, t_cmp),
                ])

        print()
        print(f"  {base_lib} vs {cmp_lib}")
        print()
        for line in render_table(rows, headers).splitlines():
            print(f"  {line}")
        print()

    # ── Times table ──
    headers = ["Operation"] + lib_names
    rows = []
    for op in operations:
        for n in scales:
            cells = [f"{op} x {n}"]
            for lib in lib_names:
                cells.append(fmt_time(results[op][n][lib]))
            rows.append(cells)

    print()
    print("  Times")
    print()
    for line in render_table(rows, headers).splitlines():
        print(f"  {line}")
    print()

    # ── Speedup vs marshmallow table ──
    baseline = lib_names[0]  # marshmallow
    compare_libs = lib_names[1:]
    headers = ["Operation"] + [f"vs {lib}" for lib in compare_libs]
    rows = []
    for op in operations:
        for n in scales:
            t_base = results[op][n][baseline]
            cells = [f"{op} x {n}"]
            for lib in compare_libs:
                cells.append(speedup_str(t_base, results[op][n][lib]))
            rows.append(cells)

    print(f"  Speedup (vs {baseline})")
    print()
    for line in render_table(rows, headers).splitlines():
        print(f"  {line}")
    print()


if __name__ == "__main__":
    main()
