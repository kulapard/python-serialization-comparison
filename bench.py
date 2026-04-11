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

import marshmallow as ma
import marshmallow.fields as mf
import marshmallow_recipe as mr
import pydantic

from models import (
    Author,
    Clause,
    Comment,
    Contract,
    Currency,
    Department,
    Employee,
    Organization,
    OrgType,
    Priority,
    Project,
    Reaction,
    Role,
    Status,
    SubTask,
    Task,
    Team,
    Terms,
    make_organization,
    make_organization_dict,
)

# ──────────────────────────────────────────────
# 1. marshmallow schemas (hand-written, 10 levels)
# ──────────────────────────────────────────────

class MaAuthorSchema(ma.Schema):  # L10
    id = mf.String(required=True)
    username = mf.String(required=True)
    display_name = mf.String(required=True)
    email = mf.String(required=True)
    verified = mf.Boolean(required=True)
    role = mf.Enum(Role, by_value=True)
    reputation = mf.Integer(required=True)
    joined_at = mf.DateTime(required=True)
    bio = mf.String(required=True)
    avatar_url = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Author(**data)


class MaReactionSchema(ma.Schema):  # L9
    id = mf.String(required=True)
    emoji = mf.String(required=True)
    label = mf.String(required=True)
    created_at = mf.DateTime(required=True)
    author = mf.Nested(MaAuthorSchema, required=True)
    count = mf.Integer(required=True)
    active = mf.Boolean(required=True)
    category = mf.String(required=True)
    weight = mf.Decimal(required=True, as_string=True)
    source = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Reaction(**data)


class MaCommentSchema(ma.Schema):  # L8
    id = mf.String(required=True)
    text = mf.String(required=True)
    created_at = mf.DateTime(required=True)
    updated_at = mf.DateTime(required=True)
    edited = mf.Boolean(required=True)
    author_name = mf.String(required=True)
    likes = mf.Integer(required=True)
    language = mf.String(required=True)
    status = mf.Enum(Status, by_value=True)
    reactions = mf.List(mf.Nested(MaReactionSchema), required=True)
    parent_id = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Comment(**data)


class MaSubTaskSchema(ma.Schema):  # L7
    id = mf.String(required=True)
    title = mf.String(required=True)
    description = mf.String(required=True)
    done = mf.Boolean(required=True)
    priority = mf.Enum(Priority, by_value=True)
    estimated_hours = mf.Decimal(required=True, as_string=True)
    actual_hours = mf.Decimal(required=True, as_string=True)
    assignee = mf.String(required=True)
    created_at = mf.Date(required=True)
    comment = mf.Nested(MaCommentSchema, required=True)
    due_date = mf.Date(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return SubTask(**data)


class MaClauseSchema(ma.Schema):  # L7
    id = mf.String(required=True)
    title = mf.String(required=True)
    body = mf.String(required=True)
    section = mf.String(required=True)
    mandatory = mf.Boolean(required=True)
    version = mf.Integer(required=True)
    effective_date = mf.Date(required=True)
    language = mf.String(required=True)
    category = mf.String(required=True)
    penalty_amount = mf.Decimal(load_default=None, dump_default=None, as_string=True)

    @ma.post_load
    def make(self, data, **_):
        return Clause(**data)


class MaTaskSchema(ma.Schema):  # L6
    id = mf.String(required=True)
    title = mf.String(required=True)
    description = mf.String(required=True)
    priority = mf.Enum(Priority, by_value=True)
    status = mf.Enum(Status, by_value=True)
    created_at = mf.DateTime(required=True)
    due_date = mf.Date(required=True)
    estimated_hours = mf.Decimal(required=True, as_string=True)
    assignee = mf.String(required=True)
    tags = mf.List(mf.String(), required=True)
    subtasks = mf.List(mf.Nested(MaSubTaskSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Task(**data)


class MaTermsSchema(ma.Schema):  # L6
    id = mf.String(required=True)
    title = mf.String(required=True)
    effective_date = mf.Date(required=True)
    expiry_date = mf.Date(required=True)
    governing_law = mf.String(required=True)
    jurisdiction = mf.String(required=True)
    version = mf.Integer(required=True)
    auto_renew = mf.Boolean(required=True)
    notice_days = mf.Integer(required=True)
    clauses = mf.List(mf.Nested(MaClauseSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Terms(**data)


class MaProjectSchema(ma.Schema):  # L5
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    budget = mf.Decimal(required=True, as_string=True)
    spent = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    started_at = mf.Date(required=True)
    status = mf.Enum(Status, by_value=True)
    owner = mf.String(required=True)
    tags = mf.List(mf.String(), required=True)
    tasks = mf.List(mf.Nested(MaTaskSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Project(**data)


class MaContractSchema(ma.Schema):  # L5
    id = mf.String(required=True)
    title = mf.String(required=True)
    contract_number = mf.String(required=True)
    signed_at = mf.DateTime(required=True)
    value = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    status = mf.Enum(Status, by_value=True)
    counterparty = mf.String(required=True)
    renewable = mf.Boolean(required=True)
    terms = mf.Nested(MaTermsSchema, required=True)
    notes = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Contract(**data)


class MaEmployeeSchema(ma.Schema):  # L4
    id = mf.String(required=True)
    name = mf.String(required=True)
    email = mf.String(required=True)
    phone = mf.String(required=True)
    hired_at = mf.Date(required=True)
    salary = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    role = mf.Enum(Role, by_value=True)
    active = mf.Boolean(required=True)
    contract = mf.Nested(MaContractSchema, required=True)
    projects = mf.List(mf.Nested(MaProjectSchema), required=True)
    tags = mf.List(mf.String(), required=True)
    note = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Employee(**data)


class MaTeamSchema(ma.Schema):  # L3
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    lead_name = mf.String(required=True)
    lead_email = mf.String(required=True)
    created_at = mf.Date(required=True)
    status = mf.Enum(Status, by_value=True)
    room = mf.String(required=True)
    max_size = mf.Integer(required=True)
    members = mf.List(mf.Nested(MaEmployeeSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Team(**data)


class MaDepartmentSchema(ma.Schema):  # L2
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    floor = mf.Integer(required=True)
    budget = mf.Decimal(required=True, as_string=True)
    head_name = mf.String(required=True)
    head_email = mf.String(required=True)
    status = mf.Enum(Status, by_value=True)
    created_at = mf.Date(required=True)
    teams = mf.List(mf.Nested(MaTeamSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Department(**data)


class MaOrganizationSchema(ma.Schema):  # L1
    id = mf.String(required=True)
    name = mf.String(required=True)
    legal_name = mf.String(required=True)
    org_type = mf.Enum(OrgType, by_value=True)
    status = mf.Enum(Status, by_value=True)
    founded = mf.Date(required=True)
    tax_id = mf.String(required=True)
    country = mf.String(required=True)
    employee_count = mf.Integer(required=True)
    annual_revenue = mf.Decimal(required=True, as_string=True)
    departments = mf.List(mf.Nested(MaDepartmentSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Organization(**data)


# ──────────────────────────────────────────────
# 2. marshmallow-recipe — auto-generated from dataclasses
# ──────────────────────────────────────────────
# mr.dump(obj), mr.load(Cls, data)
# mr.nuked.dump(Cls, obj), mr.nuked.load(Cls, data)


# ──────────────────────────────────────────────
# 3. pydantic TypeAdapter (reuses shared dataclasses)
# ──────────────────────────────────────────────

OrgAdapter = pydantic.TypeAdapter(Organization)


# ──────────────────────────────────────────────
# 4. Benchmark harness
# ──────────────────────────────────────────────

def bench(fn, *, warmup: int = 5, min_rounds: int = 10, budget: float = 2.0):
    """Return median execution time in seconds.

    Runs at least *min_rounds* iterations but stops after *budget* seconds
    of measurement to keep deep/large benchmarks practical.
    """
    for _ in range(warmup):
        fn()
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
# 5. Runners
# ──────────────────────────────────────────────

def run_dump_marshmallow(n: int):
    schema = MaOrganizationSchema()
    objs = [make_organization() for _ in range(n)]
    return bench(lambda: [schema.dump(o) for o in objs])


def run_load_marshmallow(n: int):
    schema = MaOrganizationSchema()
    dicts = [make_organization_dict() for _ in range(n)]
    return bench(lambda: [schema.load(d) for d in dicts])


def run_dump_mr(n: int):
    objs = [make_organization() for _ in range(n)]
    return bench(lambda: [mr.dump(o) for o in objs])


def run_load_mr(n: int):
    dicts = [make_organization_dict() for _ in range(n)]
    return bench(lambda: [mr.load(Organization, d) for d in dicts])


def run_dump_mr_nuked(n: int):
    objs = [make_organization() for _ in range(n)]
    return bench(lambda: [mr.nuked.dump(Organization, o) for o in objs])


def run_load_mr_nuked(n: int):
    dicts = [make_organization_dict() for _ in range(n)]
    return bench(lambda: [mr.nuked.load(Organization, d) for d in dicts])


def run_dump_pydantic(n: int):
    objs = [make_organization() for _ in range(n)]
    return bench(lambda: [OrgAdapter.dump_python(o) for o in objs])


def run_load_pydantic(n: int):
    dicts = [make_organization_dict() for _ in range(n)]
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

    scales = [1, 100, 1000]
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
